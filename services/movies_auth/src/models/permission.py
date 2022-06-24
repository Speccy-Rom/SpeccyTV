import uuid

from sqlalchemy.dialects.postgresql import UUID

from app import db
from core import config
from .additions.partitions import get_create_user_permission_partitions_cmds
from utils.cache.group import cache_invalidate_group, delete_items


def create_user_permission_partitions(target, connection, **kw):
    for cmd in get_create_user_permission_partitions_cmds(config.DB_USERS_PARTITIONS_NUM):
        connection.execute(cmd)
    pass


user_permission = db.Table(
    'user_permission',
    db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('content.users.id'), primary_key=True),
    db.Column('permission_id', UUID(as_uuid=True), db.ForeignKey('content.permissions.id'), primary_key=True),
    schema='content',
    postgresql_partition_by='HASH (user_id)',
    listeners=[('after_create', create_user_permission_partitions)]
)


class Permission(db.Model):
    __tablename__ = 'permissions'
    __table_args__ = {'schema': 'content'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    description = db.Column(db.String(256), nullable=True)

    def __repr__(self):
        return f'<Permission {self.name} ({self.id})>'


user_role = db.Table(
    'user_role',
    db.Column('user_id', UUID(as_uuid=True), db.ForeignKey('content.users.id'), primary_key=True),
    db.Column('role_id', UUID(as_uuid=True), db.ForeignKey('content.roles.id'), primary_key=True),
    schema='content'
)


role_permission = db.Table(
    'role_permission',
    db.Column('role_id', UUID(as_uuid=True), db.ForeignKey('content.roles.id'), primary_key=True),
    db.Column('permission_id', UUID(as_uuid=True), db.ForeignKey('content.permissions.id'), primary_key=True),
    schema='content'
)


class Role(db.Model):
    __tablename__ = 'roles'
    __table_args__ = {'schema': 'content'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    description = db.Column(db.String(256), nullable=True)
    permissions = db.relationship('Permission', secondary=role_permission, lazy='dynamic')

    def __repr__(self):
        return f'<Role {self.name} ({self.id})>'

    def has_permission(self, permission: Permission) -> bool:
        return self.permissions.filter(role_permission.c.permission_id == permission.id).count() > 0

    @cache_invalidate_group('combined_permissions')
    def add_permission(self, permission: Permission):
        if not self.has_permission(permission):
            self.permissions.append(permission)

    @cache_invalidate_group('combined_permissions')
    def remove_permission(self, permission: Permission):
        if self.has_permission(permission):
            self.permissions.remove(permission)


class CacheResetDBListener:
    @classmethod
    def before_commit(cls, session):
        session._should_invalidate_cache = False
        for obj in session.deleted:
            if isinstance(obj, Permission) or isinstance(obj, Role):
                session._should_invalidate_cache = True
                return

    @classmethod
    def after_commit(cls, session):
        if session._should_invalidate_cache:
            delete_items(match='*_combined_permissions')
        session._should_invalidate_cache = False


db.event.listen(db.session, 'before_commit', CacheResetDBListener.before_commit)
db.event.listen(db.session, 'after_commit', CacheResetDBListener.after_commit)
