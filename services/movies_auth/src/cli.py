import os

import click
import sqlalchemy

from core.db import db
from models.permission import Permission, Role
from models.users import User
from utils.permissions import PermissionNames, RoleNames
from app import app as _app


_permissions = [
    {
        'name': PermissionNames.ALL_ALL,
        'description': "Allows to do everything with everything (superuser permission)"
    },
    {
        'name': PermissionNames.PERMISSIONS_ADMIN,
        'description': "Allows to add, modify and delete roles and permissions."
    }
]

_roles = [
    {
        'name': RoleNames.SUPERUSER,
        'description': "Superuser is allowed to do everything with everything."
    }
]


@_app.cli.group()
def app():
    """Some utilities for application"""
    pass


def _add_to_db_if_not_exists(item: db.Model, *check_fields: str):
    item_type = type(item)
    existence_check_cond = {field: getattr(item, field) for field in check_fields}
    if not item_type.query.filter_by(**existence_check_cond).first():
        db.session.add(item)
        db.session.commit()


@app.command()
@click.option('-s', '--with-superuser', is_flag=True, help='Create superuser')
@click.pass_context
def init(ctx, with_superuser):
    """Initialize app (create roles and permissions, optional superuser etc.)"""
    for permission in _permissions:
        _add_to_db_if_not_exists(Permission(**permission), 'name')

    for role in _roles:
        _add_to_db_if_not_exists(Role(**role), 'name')

    superuser_role = Role.query.filter_by(name=RoleNames.SUPERUSER).first()
    superuser_permission = Permission.query.filter_by(name=PermissionNames.ALL_ALL).first()
    if not superuser_role.has_permission(superuser_permission):
        superuser_role.add_permission(superuser_permission)
        db.session.commit()

    if with_superuser:
        # We had some problems with prompt options calling ctx.invoke(create_superuser), so
        # as a quick dirty workaround here we call create_superuser via os.system()
        if os.system('flask superuser create'):
            raise RuntimeError('"superuser create" failed')

    print('App initialization done.')


@_app.cli.group()
def superuser():
    """Superuser stuff"""
    pass


@superuser.command('create')
@click.option('--email', prompt=True)
@click.option('--first-name', prompt=True)
@click.option('--last-name', prompt=True)
@click.option('--password', prompt=True, hide_input=True)
def create_superuser(email, first_name, last_name, password):
    """Create superuser"""
    print('Creating superuser...')
    try:
        new_user = User(email=email, first_name=first_name, last_name=last_name, password=password)
        db.session.add(new_user)
        superuser_role = Role.query.filter_by(name=RoleNames.SUPERUSER).first()
        if not superuser_role:
            raise RuntimeError("Superuser role not found. You must create it first by 'flask app init'")
        new_user.add_role(superuser_role)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        raise RuntimeError("Such superuser can't be created")

    print('Superuser created!')
    return 0


@superuser.command('delete')
@click.option('--email', prompt=True)
def delete_superuser(email):
    """Delete superuser"""
    user = User.query.filter_by(email=email).first()
    if not user:
        print('Superuser <{}> not found'.format(email))
        return 0
    if not user.check_permissions({'any': [PermissionNames.ALL_ALL]}):
        print('User <{}> is not superuser'.format(email))
        return 1
    db.session.delete(user)
    db.session.commit()

    print('Superuser deleted')
    return 0
