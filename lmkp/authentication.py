from base64 import standard_b64decode
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.security import effective_principals
from pyramid.httpexceptions import HTTPUnauthorized
from sqlalchemy.orm.exc import NoResultFound

from lmkp.models.database_objects import (
    Profile,
    User,
    users_profiles,
)
from lmkp.models.meta import DBSession as Session
from lmkp.security import group_finder
from lmkp.views.views import get_current_profile


class CustomAuthenticationPolicy(AuthTktAuthenticationPolicy):
    """

    A custom authentication policy that considers HTTP Basic Authentication as
    well as the default Pyramid authentication policy.
    Any request with HTTP Basic Authentication ignores the default policy and
    considers the submitted login and password only!
    The HTTP Basic Authentication ability is required for external application
    like the QGIS plugin to upload new activities.

    """

    def __init__(self, security_string, ** kwargs):
        AuthTktAuthenticationPolicy.__init__(self, security_string, ** kwargs)

    def authenticated_userid(self, request):
        # First handle request made with HTTP Basic Authentication.
        # Such request can e.g. come from external clients like a QGIS plugin
        credentials = self._get_basicauth_credentials(request)
        if credentials is not None:
            if User.check_password(
                    credentials['login'], credentials['password']):
                # Return the user id if the login and password are correct
                return credentials['login']
            else:
                raise HTTPUnauthorized()

        return AuthTktAuthenticationPolicy.authenticated_userid(self, request)

    def unauthenticated_userid(self, request):
        credentials = self._get_basicauth_credentials(request)
        if credentials is not None:
            return credentials['login']
        return AuthTktAuthenticationPolicy.unauthenticated_userid(
            self, request)

    def effective_principals(self, request):
        userid = self.authenticated_userid(request)
        if userid is not None:
            groups = group_finder(userid, request)
            # If the user is a moderator check the currently selected profile
            if len(groups) > 0 and 'group:moderators' in groups:
                profile = get_current_profile(request)
                # Try to find the profile in the list of profiles associated to
                # current user
                profile_query = Session.query(
                    Profile.code
                ).\
                    join(users_profiles).\
                    join(User).\
                    filter(User.username == userid).\
                    filter(Profile.code == profile)
                try:
                    profile_query.one()
                except NoResultFound:
                    # Profile not found: User is not moderator for current
                    # profile, remove group 'moderator' from principals
                    principals = AuthTktAuthenticationPolicy.\
                        effective_principals(self, request)
                    if 'group:moderators' in principals:
                        principals.remove('group:moderators')
                    return principals
        # In all other cases use Pyramid's default authentication policy
        return AuthTktAuthenticationPolicy.effective_principals(self, request)

    def _get_basicauth_credentials(self, request):
        authorization = request.authorization

        if authorization is not None:
            try:
                credentials = standard_b64decode(
                    request.authorization[1]).split(":")
                return {'login': credentials[0], 'password': credentials[1]}
            except TypeError:
                pass

        return None


def get_user_privileges(request):
    """
    Get the privileges of the current user.

    Returns a tuple indicating if the user is logged in and if the user
    has moderation rights for the current profile.

    Args:
        ``request`` (pyramid.request): A Pyramid Request object.

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
