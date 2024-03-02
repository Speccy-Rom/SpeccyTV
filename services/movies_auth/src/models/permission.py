import uuid

from sqlalchemy.dialects.postgresql import UUID

from app import db
from core import config
from .additions.partitions import get_create_user_permission_partitions_cmds
from utils.cache.group import cache_invalidate_group, delete_items


# Function to create user permission partitions
def create_user_permission_partitions(target, connection, **kw):
    """
    This function creates user permission partitions.

    Args:
        target: The target table to create partitions for.
        connection: The database connection.
        **kw: Additional keyword arguments.
    """
    for cmd in get_create_user_permission_partitions_cmds(
        config.DB_USERS_PARTITIONS_NUM
    ):
        connection.execute(cmd)


# Definition of the user_permission table
user_permission = db.Table(
    'user_permission',
    db.Column(
        'user_id',
        UUID(as_uuid=True),
        db.ForeignKey('content.users.id'),
        primary_key=True,
    ),
    db.Column(
        'permission_id',
        UUID(as_uuid=True),
        db.ForeignKey('content.permissions.id'),
        primary_key=True,
    ),
    schema='content',
    postgresql_partition_by='HASH (user_id)',
    listeners=[('after_create', create_user_permission_partitions)],
)


# Definition of the Permission model
class Permission(db.Model):
    """
    This class represents the Permission model.

    Attributes:
        id: The unique identifier of the permission.
        name: The name of the permission.
        description: The description of the permission.
    """

    __tablename__ = 'permissions'
    __table_args__ = {'schema': 'content'}

    id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    description = db.Column(db.String(256), nullable=True)

    def __repr__(self):
        return f'<Permission {self.name} ({self.id})>'


# Definition of the user_role table
user_role = db.Table(
    'user_role',
    db.Column(
        'user_id',
        UUID(as_uuid=True),
        db.ForeignKey('content.users.id'),
        primary_key=True,
    ),
    db.Column(
        'role_id',
        UUID(as_uuid=True),
        db.ForeignKey('content.roles.id'),
        primary_key=True,
    ),
    schema='content',
)

# Definition of the role_permission table
role_permission = db.Table(
    'role_permission',
    db.Column(
        'role_id',
        UUID(as_uuid=True),
        db.ForeignKey('content.roles.id'),
        primary_key=True,
    ),
    db.Column(
        'permission_id',
        UUID(as_uuid=True),
        db.ForeignKey('content.permissions.id'),
        primary_key=True,
    ),
    schema='content',
)


# Definition of the Role model
class Role(db.Model):
    """
    This class represents the Role model.

    Attributes:
        id: The unique identifier of the role.
        name: The name of the role.
        description: The description of the role.
        permissions: The permissions associated with the role.
    """

    __tablename__ = 'roles'
    __table_args__ = {'schema': 'content'}

    id = db.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    description = db.Column(db.String(256), nullable=True)
    permissions = db.relationship(
        'Permission', secondary=role_permission, lazy='dynamic'
    )

    def __repr__(self):
        return f'<Role {self.name} ({self.id})>'

    # Method to check if a role has a permission
    def has_permission(self, permission: Permission) -> bool:
        """
        This method checks if the role has a specific permission.

        Args:
            permission: The permission to check.

        Returns:
            bool: True if the role has the permission, False otherwise.
        """
        return (
            self.permissions.filter(
                role_permission.c.permission_id == permission.id
            ).count()
            > 0
        )

    # Method to add a permission to a role
    @cache_invalidate_group('combined_permissions')
    def add_permission(self, permission: Permission):
        """
        This method adds a permission to the role.

        Args:
            permission: The permission to add.
        """
        if not self.has_permission(permission):
            self.permissions.append(permission)

    # Method to remove a permission from a role
    @cache_invalidate_group('combined_permissions')
    def remove_permission(self, permission: Permission):
        """
        This method removes a permission from the role.

        Args:
            permission: The permission to remove.
        """
        if self.has_permission(permission):
            self.permissions.remove(permission)


# Definition of the CacheResetDBListener class
class CacheResetDBListener:
    """
    This class represents a listener that resets the cache before and after a database commit.
    """

    @classmethod
    def before_commit(cls, session):
        """
        This method is called before a database commit.

        Args:
            session: The database session.
        """
        session._should_invalidate_cache = False
        for obj in session.deleted:
            if isinstance(obj, (Permission, Role)):
                session._should_invalidate_cache = True
                return

    @classmethod
    def after_commit(cls, session):
        """
        This method is called after a database commit.

        Args:
            session: The database session.
        """
        if session._should_invalidate_cache:
            delete_items(match='*_combined_permissions')
        session._should_invalidate_cache = False


# Adding the CacheResetDBListener to the database events
db.event.listen(db.session, 'before_commit', CacheResetDBListener.before_commit)
db.event.listen(db.session, 'after_commit', CacheResetDBListener.after_commit)
