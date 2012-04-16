from base64 import standard_b64decode
from lmkp.models.database_objects import User
from lmkp.security import group_finder
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
        credentials = self._get_basicauth_credentials(request)
        if credentials is not None:
            if User.check_password(credentials['login'], credentials['password']):
                # Return the user id if the login and password are correct
                return credentials['login']
            else:
                # Else return none
                return None

        return AuthTktAuthenticationPolicy.authenticated_userid(self, request)

    def unauthenticated_userid(self, request):
        credentials = self._get_basicauth_credentials(request)
        if credentials is not None:
            return credentials['login']
        return AuthTktAuthenticationPolicy.unauthenticated_userid(self, request)

    def effective_principals(self, request):
        credentials = self._get_basicauth_credentials(request)

        if credentials is not None:
            userid = None
            groups = None
            # Default principal is Everyone
            effective_principals = [Everyone]
            # Get the authenticated user id
            userid = self.authenticated_userid(request)
            if userid is not None:
                groups = group_finder(userid, request)
                if groups is not None:
                    effective_principals.append(Authenticated)
                    effective_principals.append(userid)
                    effective_principals.extend(groups)
                    return effective_principals
            # If the user id is none return the Everyone principals
            else:
                return effective_principals


        # In all other cases use Pyramid's default authentication policy
        return AuthTktAuthenticationPolicy.effective_principals(self, request)

    def _get_basicauth_credentials(self, request):
        authorization = request.authorization

        if authorization is not None:
            credentials = standard_b64decode(request.authorization[1]).split(":")
            return {'login': credentials[0], 'password': credentials[1]}

        return None
