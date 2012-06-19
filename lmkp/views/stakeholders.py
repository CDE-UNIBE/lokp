from pyramid.i18n import TranslationStringFactory
from lmkp.models.meta import DBSession as Session
from lmkp.views.stakeholder_protocol import StakeholderProtocol
import logging
from pyramid.httpexceptions import HTTPForbidden
from pyramid.security import ACLAllowed
from pyramid.security import authenticated_userid
from pyramid.security import effective_principals
from pyramid.security import has_permission
from pyramid.view import view_config

log = logging.getLogger(__name__)

_ = TranslationStringFactory('lmkp')

stakeholder_protocol = StakeholderProtocol(Session)

@view_config(route_name='stakeholders_create', renderer='json')
def create(request):
    """
    Add a new stakeholder.
    Implements the create functionality (HTTP POST) in the CRUD model

    Test the POST request e.g. with
    curl --data @line.json http://localhost:6543/stakeholders

    """

    # Check if the user is logged in and he/she has sufficient user rights
    userid = authenticated_userid(request)
    print effective_principals(request)

    if userid is None:
        return HTTPForbidden()
    if not isinstance(has_permission('edit', request.context, request), ACLAllowed):
        return HTTPForbidden()

    return stakeholder_protocol.create(request)