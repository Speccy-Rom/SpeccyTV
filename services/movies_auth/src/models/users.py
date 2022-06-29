import uuid
from hashlib import sha512

from sqlalchemy.dialects.postgresql import UUID, INET

from app import db
from core import config
from .permission import user_permission, Permission, user_role, Role
from .additions.partitions import get_create_users_partitions_cmds
from utils.cache.base import cache_invalidate


def create_partitions(target, connection, **kw):
    for cmd in get_create_users_partitions_cmds(config.DB_USERS_PARTITIONS_NUM):
        connection.execute(cmd)


class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'content',
                      'postgresql_partition_by': 'HASH (id)',
                      'listeners': [('after_create', create_partitions)]}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    password = db.Column(db.String, nullable=False)
    permissions = db.relationship('Permission', secondary=user_permission, lazy='dynamic')
    roles = db.relationship('Role', secondary=user_role, lazy='dynamic')
    logins = db.relationship('UserLogin')

    def __init__(self, email: str, first_name: str, last_name: str, password: str):
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.set_password(password)

    def check_password(self, raw_password):
        return self.password == self._make_password(raw_password)

    def _make_password(self, raw_password):
        return sha512(f'{raw_password}salt'.encode()).hexdigest()

    def set_password(self, raw_password) -> None:
        self.password = self._make_password(raw_password)

    def has_permission(self, permission: Permission):
        return self.permissions.filter(user_permission.c.permission_id == permission.id).count() > 0

    @cache_invalidate('combined_permissions')
    def add_permission(self, permission):
        if not self.has_permission(permission):
            self.permissions.append(permission)

    @cache_invalidate('combined_permissions')
    def remove_permission(self, permission: Permission):
        if self.has_permission(permission):
            self.permissions.remove(permission)

    def has_role(self, role: Role):
        return self.roles.filter(user_role.c.role_id == role.id).count() > 0

    @cache_invalidate('combined_permissions')
    def add_role(self, role: Role):
        if not self.has_role(role):
            self.roles.append(role)

    @cache_invalidate('combined_permissions')
    def remove_role(self, role: Role):
        if self.has_role(role):
            self.roles.remove(role)

    def _get_combined_permissions_set(self):
        permissions = set()
        for role in self.roles.all():
            permissions.update(role.permissions.all())
        permissions.update(self.permissions.all())
        return permissions

    @property
    def combined_permissions(self):
        ordered_permissions = sorted(self._get_combined_permissions_set(), key=lambda permission: permission.name)
        return ordered_permissions

    # query example: {'any': ['packs_ext', {'all': ['cloud_people', 'electric_edwards']}]}
    @classmethod
    def check_permissions_set(cls, query: dict, permissions: set[str]) -> bool:
        key, value = next(iter(query.items()))
        conditions = (cls.check_permissions_set(c, permissions) if isinstance(c, dict) else str(c) in permissions for c in
                      value)
        return any(conditions) if key == 'any' else all(conditions)

    # query example: see check_permissions_set above
    def check_permissions(self, query: dict) -> bool:
        permissions_set = {permission.name for permission in self._get_combined_permissions_set()}
        return self.check_permissions_set(query, permissions_set)

    def __repr__(self):
        return f'{self.__class__.__name__}(email={self.email}, first_name={self.first_name}, ...)'


class UserLogin(db.Model):
    __tablename__ = 'user_logins'
    __table_args__ = {'schema': 'content'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ip_address = db.Column(INET, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    user = db.Column(UUID(as_uuid=True), db.ForeignKey('content.users.id'))

    def __init__(self, ip_address, time, user):
        self.ip_address = ip_address
        self.time = time
        self.user = user

    def __repr__(self):
        return f'{self.__class__.__name__}(ip_address={self.ip_address!r}, time={self.time!r}, ...)'


class SocialAccount(db.Model):
    __tablename__ = 'social_account'
    __table_args__ = (
        db.UniqueConstraint('social_id', 'social_name', name='social_pk'),
        {'schema': 'content'}
    )

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('content.users.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship(User, backref=db.backref('social_accounts', lazy=True))

    social_id = db.Column(db.Text, nullable=False)
    social_name = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<SocialAccount {self.social_name}:{self.user_id}>'
