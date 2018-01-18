from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.security import effective_principals, Allow, Everyone
from sqlalchemy.orm.exc import NoResultFound

from lokp.models import Group, users_groups, User, DBSession, Profile, \
    users_profiles
from lokp.utils.views import get_current_profile


class CustomAuthenticationPolicy(AuthTktAuthenticationPolicy):
    """

    A custom authentication policy that considers HTTP Basic Authentication as
    well as the default Pyramid authentication policy.
    Any request with HTTP Basic Authentication ignores the default policy and
    considers the submitted login and password only!
    The HTTP Basic Authentication ability is required for external application
    like the QGIS plugin to upload new activities.

    """
    def effective_principals(self, request):
        userid = self.authenticated_userid(request)
        if userid is not None:
            groups = group_finder(userid, request)
            # If the user is a moderator check the currently selected profile
            if len(groups) > 0 and 'group:moderators' in groups:
                profile = get_current_profile(request)
                # Try to find the profile in the list of profiles associated to
                # current user
                profile_query = DBSession.query(
                    Profile.code
                ). \
                    join(users_profiles). \
                    join(User). \
                    filter(User.username == userid). \
                    filter(Profile.code == profile)
                try:
                    profile_query.one()
                except NoResultFound:
                    # Profile not found: User is not moderator for current
                    # profile, remove group 'moderator' from principals
                    principals = AuthTktAuthenticationPolicy. \
                        effective_principals(self, request)
                    if 'group:moderators' in principals:
                        principals.remove('group:moderators')
                    return principals
        # In all other cases use Pyramid's default authentication policy
        return AuthTktAuthenticationPolicy.effective_principals(self, request)


def get_user_privileges(request):
    """
    Get the privileges of the current user.

    Returns a tuple indicating if the user is logged in and if the user
    has moderation rights for the current profile.

    Args:
        ``request`` (pyramid.request): A :term:`Pyramid` Request object.

    Returns:
        ``bool`` or ``None``. Returns ``True`` if the user is logged in,
        ``False`` or ``None`` if not.

        ``bool`` or ``None``. Returns ``True`` if the user has
        moderation privileges for the current profile, `False`` or
        ``None`` if not.
    """
    principals = effective_principals(request)
    if principals:
        return (
            'system.Authenticated' in principals,
            'group:moderators' in principals
        )
    return None, None


def group_finder(username, request):
    """
    Finds and returns all user groups for a certain user name.
    """
    if username:
        groupQuery = DBSession.query(
            Group.name
        ). \
            join(users_groups). \
            join(User). \
            filter(User.username == username)
        return ["group:%s" % group.name for group in groupQuery.all()]
    return []


class RootFactory(object):
    """
    Static ACL.
    """
    __acl__ = [
        (Allow, Everyone, 'view'),
        (Allow, 'group:administrators', ('administer', 'moderate', 'edit', 'view')),
        (Allow, 'group:moderators', ('moderate', 'edit', 'view')),
        (Allow, 'group:editors', ('edit', 'view')),
        (Allow, 'group:translators', 'translate'),
    ]

    def __init__(self, request):
        pass
