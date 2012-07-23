from base64 import standard_b64decode
from lmkp.models.database_objects import User
from lmkp.models.meta import DBSession as Session
from lmkp.security import group_finder
from lmkp.views.profile import get_current_profile
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import Everyone
from pyramid.security import Authenticated

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
            if User.check_password(credentials['login'], credentials['password']):
                # Return the user id if the login and password are correct
                return credentials['login']

        return AuthTktAuthenticationPolicy.authenticated_userid(self, request)

    def unauthenticated_userid(self, request):
        credentials = self._get_basicauth_credentials(request)
        if credentials is not None:
            return credentials['login']
        return AuthTktAuthenticationPolicy.unauthenticated_userid(self, request)

    def effective_principals(self, request):
        userid = self.authenticated_userid(request)
        if userid is not None:
            groups = group_finder(userid, request)

            # If the user is a moderator check the selected profile
            if groups is not None and groups[0] == 'group:moderators':
                # Get the user
                user = Session.query(User).filter(User.username == userid).first()
                # and the current profile from the request
                profile = get_current_profile(request)
                # Check if the requested profile is assigned to this user
                if profile in [p.code for p in user.profiles]:
                    # If the set profile is assigned to the current moderator,
                    # the usual principals are used
                    return AuthTktAuthenticationPolicy.effective_principals(self, request)
                else:
                    # In other cases the moderator gets only editor rights:
                    # Default principal is Everyone
                    effective_principals = [Everyone]
                    # Append the current user and the editor group to the principals
                    effective_principals.append(Authenticated)
                    effective_principals.append(userid)
                    effective_principals.extend(['group:editors'])
                    return effective_principals

        # In all other cases use Pyramid's default authentication policy
        return AuthTktAuthenticationPolicy.effective_principals(self, request)

    def _get_basicauth_credentials(self, request):
        authorization = request.authorization

        if authorization is not None:
            try:
                credentials = standard_b64decode(request.authorization[1]).split(":")
                return {'login': credentials[0], 'password': credentials[1]}
            except TypeError:
                pass

        return None
