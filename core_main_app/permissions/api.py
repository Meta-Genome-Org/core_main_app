"""
Permissions API
"""
import collections

from django.contrib.auth.models import Permission, ContentType
from django.db.models import Q

from core_main_app.components.group import api as group_api
from core_main_app.components.user import api as user_api
from core_main_app.permissions.rights import CAN_READ_NAME, CAN_READ_CODENAME, CONTENT_TYPE_APP_LABEL,\
    CAN_WRITE_NAME, CAN_WRITE_CODENAME


def _title_to_codename(title):
    """ Change the title to a codename.

    Args:
        title:

    Returns:
    """

    # remove unnecessary spaces
    title = title.strip()
    # to lower case
    title = title.lower()
    # replace spaces by underscores
    title = title.replace(" ", "_")
    return title


def create_read_perm(title):
    """ Create read permission.

    Args:
        title

    Returns:
    """
    name = CAN_READ_NAME + " - " + title.strip()
    content_type = ContentType.objects.get(app_label=CONTENT_TYPE_APP_LABEL, model='main')
    codename = CAN_READ_CODENAME + "_" + _title_to_codename(title)
    return _create_perm(name, content_type, codename)


def create_write_perm(title):
    """ Create write permission.

    Args:
        title

    Returns:
    """
    name = CAN_WRITE_NAME + " - " + title.strip()
    content_type = ContentType.objects.get(app_label=CONTENT_TYPE_APP_LABEL, model='main')
    codename = CAN_WRITE_CODENAME + "_" + _title_to_codename(title)
    return _create_perm(name, content_type, codename)


def _create_perm(name, content_type, codename):
    """ Create permission.

    Args:
        name
        content_type
        codename

    Returns:
    """

    try:
        perm = Permission.objects.get(content_type=content_type,
                                      codename=codename)

    except Exception, ie:
        perm = Permission.objects.create(name=name,
                                         content_type=content_type,
                                         codename=codename)
        perm.save()
    return perm


def add_permission_to_user(user, permission):
    """ Add permission to user.

    Args:
        user_id
        permission

    Returns:
    """
    user.user_permissions.add(permission)
    user.save()


def add_permission_to_group(group, permission):
    """ Add permission to group.

    Args:
        group
        permission

    Returns:
    """
    group.permissions.add(permission)
    group.save()


def remove_permission_to_user(user, permission):
    """ Remove permission from user.

    Args:
        user
        permission

    Returns:
    """
    user.user_permissions.remove(permission)
    user.save()


def remove_permission_to_group(group, permission):
    """ Remove permission from group.

    Args:
        group
        permission

    Returns:
    """
    group.permissions.remove(permission)
    group.save()


def get_all_public_workspace_permission():
    """ Get all permissions related to public workspaces.

    Return:
    """
    return [str(perm.id) for perm in Permission.objects.filter((Q(group=group_api.get_default_group())
                                                                & Q(group=group_api.get_anonymous_group())),
                                                               content_type__app_label=CONTENT_TYPE_APP_LABEL,
                                                               codename__startswith=CAN_READ_CODENAME)]


def get_all_workspace_permissions_user_can_write(user_id):
    """ Get a list of permission ids of workspaces that the user has write access.

    Args:
        user_id

    Return:

    """
    user = user_api.get_user_by_id(user_id)
    return [str(perm.id) for perm in Permission.objects.filter((Q(user=user) | Q(group__in=user.groups.all())),
                                                               content_type__app_label=CONTENT_TYPE_APP_LABEL,
                                                               codename__startswith=CAN_WRITE_CODENAME)]


def get_all_workspace_permissions_user_can_read(user_id):
    """ Get a list of permission ids of workspaces that the user has read access.

    Args:
        user_id

    Return:
    """
    user = user_api.get_user_by_id(user_id)
    return [str(perm.id) for perm in Permission.objects.filter((Q(user=user) 
                                                                | Q(group__in=user.groups.all())
                                                                | (Q(group=group_api.get_default_group())
                                                                   & Q(group=group_api.get_anonymous_group()))),
                                                               content_type__app_label=CONTENT_TYPE_APP_LABEL,
                                                               codename__startswith=CAN_READ_CODENAME)]


def is_workspace_public(permission_id):
    """ Check if the workspace is public.

    Args:
        permission_id

    Returns:
    """
    permission = Permission.objects.get(pk=permission_id)
    group_anonymous = group_api.get_anonymous_group()
    group_default = group_api.get_default_group()
    return permission in group_anonymous.permissions.all() and permission in group_default.permissions.all()


def get_by_id(permission_id):
    """ Get the permission by id.

    Args:
         permission_id:
    Returns:
    """
    return Permission.objects.get(pk=permission_id)


def delete_permission(permission_id):
    """ Delete a permission.

    Args:
        permission_id:

    Return:
    """

    try:
        perm = get_by_id(permission_id)
        perm.delete()
    except Exception, e:
        pass


def get_permission_label(permission_id):
    """ Get the label of a permission.

    Args:
        permission_id:

    Return:
    """
    permission = Permission.objects.get(pk=permission_id)
    return permission.content_type.app_label + "." + permission.codename


def check_if_group_has_perm(group, permission):
    """ Check if group has permission.

    Args:
        group:
        permission:
    Returns:
    """
    return len(group.permissions.filter(id=str(permission.id))) == 1