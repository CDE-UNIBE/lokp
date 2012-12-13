import logging
from pyramid.view import view_config

log = logging.getLogger(__name__)

@view_config(route_name='request_test', renderer='lmkp:templates/request_test.mak')
def request_test(request):
    """
    Dummy view to count SQLAlchemy queries when rendering a simple HTML view.
    Should be deleted before going productive.
    """

    #userid = authenticated_userid(request)

    #userid = authenticated_userid(request)

    if request.user is not None:
        username = request.user.username

        log.debug(username)

    #principals = effective_principals(request)

    log.debug(request.effective_principals)

    log.debug(request.effective_principals)
    log.debug(request.effective_principals)
    log.debug(request.effective_principals)
    log.debug(request.effective_principals)

    return {}