from pyramid.security import Allow
from pyramid.security import Everyone

class RootFactory(object):
    """
    Extract __acl__ from database (Tables "groups" and "permissions",
    linked through "l_groups_permissions")

    This class configures the ACL (Access Control List) consisting
    of a sequence of ACEs (Access Control Entry) that define the
    permissions of user groups.

    It is called on initial loading when configurating the
    application in __init__.py
    """
    from lmkp.models.meta import DBSession
    from lmkp.models.database_objects import Group
    acl = []
    acl.append((Allow, Everyone, 'view')) # basic ACE (view permission to Everyone)
    group_query = DBSession.query(Group).all()
    for group in group_query:
        ace_permissions = []
        for permission in group.permissions:
            ace_permissions.append(permission.name)
        acl.append((Allow, "group:%s" % group.name, ace_permissions))
    __acl__ = acl
    
    def __init__(self, request):
        pass