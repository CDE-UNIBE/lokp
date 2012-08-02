from lmkp.models.meta import DBSession as Session
from lmkp.views.stakeholder_protocol import StakeholderProtocol
from lmkp.views.config import get_mandatory_keys
from lmkp.models.database_objects import *
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

    # If review decision is 'approved', make sure that all mandatory fields are
    # there
    try:
        review_decision = int(request.POST['review_decision'])
    except:
        review_decision = None

    if review_decision == 1: # Approved
        mandatory_keys = get_mandatory_keys(request, 'sh')
        # Query keys
        activity_keys = Session.query(SH_Key.key).\
            join(SH_Tag).\
            join(SH_Tag_Group, SH_Tag.fk_tag_group == SH_Tag_Group.id).\
            filter(SH_Tag_Group.stakeholder == stakeholder)
        keys = []
        for k in activity_keys.all():
            keys.append(k.key)
        for mk in mandatory_keys:
            if mk not in keys:
                return {'success': False, 'msg': 'Not all mandatory keys are provided.'}

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

    ids = stakeholder_protocol.create(request)

    response = {}
    response['data'] = [i.to_json() for i in ids]
    response['total'] = len(response['data'])

    request.response.status = 201
    return response

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