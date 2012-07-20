from lmkp.models.meta import DBSession as Session
from lmkp.views.stakeholder_protocol import StakeholderProtocol
from lmkp.models.database_objects import User
from lmkp.models.database_objects import SH_Changeset_Review
from lmkp.models.database_objects import Stakeholder
import logging
from pyramid.httpexceptions import HTTPForbidden
from pyramid.i18n import TranslationStringFactory
from pyramid.security import ACLAllowed
from pyramid.security import authenticated_userid
from pyramid.security import effective_principals
from pyramid.security import has_permission
from pyramid.view import view_config

log = logging.getLogger(__name__)

_ = TranslationStringFactory('lmkp')

stakeholder_protocol = StakeholderProtocol(Session)

@view_config(route_name='stakeholders_review', renderer='json')
def review(request):
    """
    Insert a review decision for a pending Stakeholder
    """

    # Check if the user is logged in and he/she has sufficient user rights
    userid = authenticated_userid(request)
    if userid is None:
        return {'success': False, 'msg': 'User is not logged in.'}
    if not isinstance(has_permission('moderate', request.context, request), ACLAllowed):
        return {'success': False, 'msg': 'User has no permissions to add a review.'}
    user = Session.query(User).\
            filter(User.username == authenticated_userid(request)).first()

    # Query new version of Stakeholder
    stakeholder = Session.query(Stakeholder).\
        filter(Stakeholder.stakeholder_identifier == request.POST['identifier']).\
        filter(Stakeholder.version == request.POST['version']).\
        first()
    if stakeholder is None:
        return {'success': False, 'msg': 'The Stakeholder was not found'}

    # Also query previous Stakeholder if available
    previous_stakeholder = Session.query(Stakeholder).\
        filter(Stakeholder.stakeholder_identifier == request.POST['identifier']).\
        filter(Stakeholder.version == stakeholder.changesets[0].previous_version).\
        first()

    # The user can add a review
    ret = stakeholder_protocol._add_review(
        request, stakeholder, previous_stakeholder, SH_Changeset_Review, user
    )

    return ret

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

@view_config(route_name='stakeholders_read_one', renderer='json')
def read_one(request):
    """
    Returns the feature with the requested id
    """
    uid = request.matchdict.get('uid', None)
    return stakeholder_protocol.read(request, uid=uid)


@view_config(route_name='stakeholders_read_many', renderer='json')
def read_many(request):
    """
    Reads many active activities
    """
    return stakeholder_protocol.read(request)

@view_config(route_name='stakeholders_history', renderer='json')
def stakeholders_history(request):
    uid = request.matchdict.get('uid', None)

    return stakeholder_protocol.history(request, uid=uid)