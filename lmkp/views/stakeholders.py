from lmkp.models.meta import DBSession as Session
from lmkp.config import check_valid_uuid
from lmkp.config import getTemplatePath
from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
from lmkp.views.config import get_mandatory_keys
from lmkp.views.comments import comments_sitekey
from lmkp.views.form import renderForm
from lmkp.views.form import renderReadonlyForm
from lmkp.views.form import renderReadonlyCompareForm
from lmkp.views.form import checkValidItemjson
from lmkp.views.form_config import getCategoryList
from lmkp.views.profile import get_current_profile
from lmkp.views.profile import get_current_locale
from lmkp.views.activities import _handle_spatial_parameters
from lmkp.views.views import BaseView
from lmkp.models.database_objects import *
from lmkp.authentication import checkUserPrivileges
from lmkp.views.stakeholder_review import StakeholderReview
from lmkp.views.translation import get_translated_status
import logging
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationStringFactory
from pyramid.renderers import render_to_response
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.security import ACLAllowed
from pyramid.security import authenticated_userid
from pyramid.security import has_permission
from pyramid.view import view_config

log = logging.getLogger(__name__)

_ = TranslationStringFactory('lmkp')

stakeholder_protocol3 = StakeholderProtocol3(Session)

@view_config(route_name='stakeholders_read_one_active')
def read_one_active(request):
    """
    Read one Stakeholder based on ID and return only the active version of the
    Stakeholder.
    Default output format: JSON
    """

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    uid = request.matchdict.get('uid', None)
    if check_valid_uuid(uid) is not True:
        raise HTTPNotFound()

    if output_format == 'json':
        stakeholders = stakeholder_protocol3.read_one_active(request, uid=uid)
        return render_to_response('json', stakeholders, request)
    elif output_format == 'html':
        #@TODO
        return render_to_response('json', {'HTML': 'Coming soon'}, request)
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

@view_config(route_name='stakeholders_read_one_public')
def read_one_public(request):
    """
    Read one Stakeholder based on ID and return all versions of this
    Stakeholder. Do not return any pending versions.
    Default output format: JSON
    """

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    uid = request.matchdict.get('uid', None)
    if check_valid_uuid(uid) is not True:
        raise HTTPNotFound()

    if output_format == 'json':
        stakeholders = stakeholder_protocol3.read_one(request, uid=uid,
            public=True)
        return render_to_response('json', stakeholders, request)
    elif output_format == 'html':
        #@TODO
        return render_to_response('json', {'HTML': 'Coming soon'}, request)
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

# Use route stakeholders_by_activities_all if there is no UID specified
@view_config(route_name='stakeholders_byactivities')
@view_config(route_name='stakeholders_byactivities_all')
def by_activities(request):
    """
    Read many Stakeholders based on Activities filter params and/or an Actity
    ID. Also returning Stakeholders by currently logged in user and all pending
    Stakeholders if logged in as moderator.
    Default output format: JSON
    """

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    uids = []
    uidsMatchdict = request.matchdict.get('uids', None)
    if uidsMatchdict is not None:
        uids = uidsMatchdict.split(',')

    # Remove any invalid UIDs
    for uid in uids:
        if check_valid_uuid(uid) is not True:
            uids.remove(uid)

    if output_format == 'json':
        stakeholders = stakeholder_protocol3.read_many_by_activities(request,
            public=False, uids=uids)
        return render_to_response('json', stakeholders, request)
    elif output_format == 'html':
        """
        Show a HTML representation of the Stakeholders of an Activity in a grid.
        """

        # Get page parameter from request and make sure it is valid
        page = request.params.get('page', 1)
        try:
            page = int(page)
        except TypeError:
            page = 1
        page = max(page, 1) # Page should be >= 1

        # Get pagesize parameter from request and make sure it is valid
        pageSize = request.params.get('pagesize', 10)
        try:
            pageSize = int(pageSize)
        except TypeError:
            pageSize = 10
        pageSize = max(pageSize, 1) # Page size should be >= 1
        pageSize = min(pageSize, 50) # Page size should be <= 50

        # Spatial filter: Show it only if there is no involvement filter (no
        # deal uid set)
        spatialfilter = None
        if len(uids) == 0:
            spatialfilter = _handle_spatial_parameters(request)

        # Query the items with the protocol
        items = stakeholder_protocol3.read_many_by_activities(request,
            public=False, uids=uids, limit=pageSize,
            offset=pageSize*page-pageSize)

        isLoggedIn, isModerator = checkUserPrivileges(request)

        return render_to_response(getTemplatePath(request, 'stakeholders/grid.mak'), {
            'data': items['data'] if 'data' in items else [],
            'total': items['total'] if 'total' in items else 0,
            'profile': get_current_profile(request),
            'locale': get_current_locale(request),
            'spatialfilter': spatialfilter,
            'invfilter': uids,
            'statusfilter': None,
            'currentpage': page,
            'pagesize': pageSize,
            'isModerator': isModerator
        }, request)
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

@view_config(route_name='stakeholders_byactivities_public')
@view_config(route_name='stakeholders_byactivities_all_public')
def by_activities_public(request):
    """
    Read many Stakeholders based on Activities filter params and/or an Activity
    ID. Do not return any pending versions.
    Default output format: JSON
    """

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    uids = []
    uidsMatchdict = request.matchdict.get('uids', None)
    if uidsMatchdict is not None:
        uids = uidsMatchdict.split(',')

    # Remove any invalid UIDs
    for uid in uids:
        if check_valid_uuid(uid) is not True:
            uids.remove(uid)

    if output_format == 'json':
        stakeholders = stakeholder_protocol3.read_many_by_activities(request,
            uids=uids, public=True)
        return render_to_response('json', stakeholders, request)
    elif output_format == 'html':
        #@TODO
        return render_to_response('json', {'HTML': 'Coming soon'}, request)
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

@view_config(route_name='stakeholders_read_many')
def read_many(request):
    """
    Read many, returns also pending Stakeholders by currently logged in user and
    all pending Stakeholders if logged in as moderator.
    Default output format: JSON
    """

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    if output_format == 'json':
        stakeholders = stakeholder_protocol3.read_many(request, public=False)
        return render_to_response('json', stakeholders, request)
    elif output_format == 'html':
        """
        Show a HTML representation of the Stakeholders in a grid.
        """

        # Get page parameter from request and make sure it is valid
        page = request.params.get('page', 1)
        try:
            page = int(page)
        except TypeError:
            page = 1
        page = max(page, 1) # Page should be >= 1

        # Get pagesize parameter from request and make sure it is valid
        pageSize = request.params.get('pagesize', 10)
        try:
            pageSize = int(pageSize)
        except TypeError:
            pageSize = 10
        pageSize = max(pageSize, 1) # Page size should be >= 1
        pageSize = min(pageSize, 50) # Page size should be <= 50

        items = stakeholder_protocol3.read_many(request, public=False,
            limit=pageSize, offset=pageSize*page-pageSize)
        
        statusFilter = request.params.get('status', None)
        isLoggedIn, isModerator = checkUserPrivileges(request)

        return render_to_response(getTemplatePath(request, 'stakeholders/grid.mak'), {
            'data': items['data'] if 'data' in items else [],
            'total': items['total'] if 'total' in items else 0,
            'profile': get_current_profile(request),
            'locale': get_current_locale(request),
            'spatialfilter': None,
            'invfilter': None,
            'statusfilter': statusFilter,
            'currentpage': page,
            'pagesize': pageSize,
            'isModerator': isModerator
        }, request)

    elif output_format == 'form':
        # This is used to display a new and empty form for a Stakeholder.
        if request.user is None:
            # Make sure the user is logged in
            raise HTTPForbidden()
        newInvolvement = request.params.get('inv', None)
        templateValues = renderForm(request, 'stakeholders', inv=newInvolvement)
        if isinstance(templateValues, Response):
            return templateValues
        templateValues['profile'] = get_current_profile(request)
        templateValues['locale'] = get_current_locale(request)
        return render_to_response(
            getTemplatePath(request, 'stakeholders/form.mak'),
            templateValues,
            request
        )
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

@view_config(route_name='stakeholders_read_many_public')
def read_many_public(request):
    """
    Read many, returns also pending Stakeholders by currently logged in user and
    all pending Stakeholders if logged in as moderator.
    Default output format: JSON
    """

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    if output_format == 'json':
        stakeholders = stakeholder_protocol3.read_many(request, public=True)
        return render_to_response('json', stakeholders, request)
    elif output_format == 'html':
        #@TODO
        return render_to_response('json', {'HTML': 'Coming soon'}, request)
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

@view_config(route_name='stakeholders_read_many_pending', permission='moderate')
def read_many_pending(request):
    """
    Read many pending Stakeholders.
    Default output format: JSON
    """

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    if output_format == 'json':
        stakeholders = stakeholder_protocol3.read_many_pending(request)
        return render_to_response('json', stakeholders, request)
    elif output_format == 'html':
        #@TODO
        return render_to_response('json', {'HTML': 'Coming soon'}, request)
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

@view_config(route_name='stakeholders_read_one')
def read_one(request):
    """
    Read one Stakeholder based on ID and return all versions of this
    Stakeholder. Also return pending versions by currently logged in user and
    all pending versions of this Stakeholder if logged in as moderator.
    Default output format: JSON
    """

    # Handle the parameters (locale, profile)
    bv = BaseView(request)
    bv._handle_parameters()

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    uid = request.matchdict.get('uid', None)
    if check_valid_uuid(uid) is not True:
        raise HTTPNotFound()

    if output_format == 'json':
        stakeholders = stakeholder_protocol3.read_one(request, uid=uid,
            public=False)
        return render_to_response('json', stakeholders, request)
    elif output_format == 'html':
        # Show the details of a Stakeholder by rendering the form in readonly
        # mode.
        stakeholders = stakeholder_protocol3.read_one(request, uid=uid,
            public=False, translate=False)
        version = request.params.get('v', None)
        if (stakeholders and 'data' in stakeholders
            and len(stakeholders['data']) != 0):
            for sh in stakeholders['data']:
                if 'version' in sh:
                    if version is None:
                        # If there is no version provided, show the first
                        # version visible to the user
                        version = str(sh['version'])
                    if str(sh['version']) == version:
                        templateValues = renderReadonlyForm(request, 'stakeholders', sh)
                        templateValues['profile'] = get_current_profile(request)
                        templateValues['locale'] = get_current_locale(request)

                        # Append the short uid and the uid to the templates values
                        templateValues['uid'] = uid
                        templateValues['shortuid'] = uid.split("-")[0]
                        # Append also the site key from the commenting system
                        templateValues['site_key'] = comments_sitekey(request)['site_key']
                        # and the url of the commenting system
                        templateValues['comments_url'] = request.registry.settings['lmkp.comments_url']

                        return render_to_response(
                            getTemplatePath(request, 'stakeholders/details.mak'),
                            templateValues,
                            request
                        )
        return HTTPNotFound()
    elif output_format == 'form':
        if request.user is None:
            # Make sure the user is logged in
            raise HTTPForbidden()
        # Query the Stakeholders with the given identifier
        stakeholders = stakeholder_protocol3.read_one(request, uid=uid,
            public=False, translate=False)
        version = request.params.get('v', None)
        if (stakeholders and 'data' in stakeholders
            and len(stakeholders['data']) != 0):
            for sh in stakeholders['data']:
                if 'version' in sh:
                    if version is None:
                        # If there is no version provided, show the first
                        # version visible to the user
                        version = str(sh['version'])
                    if str(sh['version']) == version:
                        templateValues = renderForm(request, 'stakeholders', itemJson=sh)
                        if isinstance(templateValues, Response):
                            return templateValues
                        templateValues['profile'] = get_current_profile(request)
                        templateValues['locale'] = get_current_locale(request)
                        return render_to_response(
                            getTemplatePath(request, 'stakeholders/form.mak'),
                            templateValues,
                            request
                        )
        return HTTPNotFound()
    elif output_format in ['review', 'compare']:
        if output_format == 'review':
            # Only moderators can see the review page.
            isLoggedIn, isModerator = checkUserPrivileges(request)
            if isLoggedIn is False or isModerator is False:
                raise HTTPForbidden()

        camefrom = request.params.get('camefrom', '')
        
        review = StakeholderReview(request)
        availableVersions = None
        recalculated = False
        defaultRefVersion, defaultNewVersion = review._get_valid_versions(
            Stakeholder, uid)
            
        refVersion = request.params.get('ref', None)
        if refVersion is not None:
            try:
                refVersion = int(refVersion)
            except ValueError:
                refVersion = None
        if refVersion is None or output_format == 'review':
            # No reference version indicated, use the default one
            # Also use the default one for review because it cannot be changed.
            refVersion = defaultRefVersion
        else:
            availableVersions = review._get_available_versions(Stakeholder, uid, 
                review=output_format=='review')
            # Check if the indicated reference version is valid
            if refVersion not in [v.get('version') for v in availableVersions]:
                refVersion = defaultRefVersion
        
        newVersion = request.params.get('new', None)
        if newVersion is not None:
            try:
                newVersion = int(newVersion)
            except ValueError:
                newVersion = None
        if newVersion is None:
            # No new version indicated, use the default one
            newVersion = defaultNewVersion
        else:
            if availableVersions is None:
                availableVersions = review._get_available_versions(Stakeholder, 
                    uid, review=output_format=='review')
            # Check if the indicated new version is valid
            if newVersion not in [v.get('version') for v in availableVersions]:
                newVersion = defaultNewVersion
                
        if output_format == 'review':
            # If the Stakeholders are to be reviewed, only the changes which 
            # were applied to the newVersion are of interest
            stakeholders, recalculated = review.get_comparison(Stakeholder, uid, 
                refVersion, newVersion)
        else:
            # If the Stakeholders are compared, the versions as they are stored
            # in the database are of interest, without any recalculation
            stakeholders = [
                stakeholder_protocol3.read_one_by_version(request, uid, 
                    refVersion, translate=False
                ),
                stakeholder_protocol3.read_one_by_version(request, uid, 
                    newVersion, translate=False
                )
            ]
        templateValues = renderReadonlyCompareForm(request, 'stakeholders', 
            stakeholders[0], stakeholders[1], review=output_format=='review')
        # Collect metadata for the reference version
        refMetadata = {}
        if stakeholders[0] is not None:
            refMetadata = stakeholders[0].get_metadata(request)
        # Collect metadata and missing keys for the new version
        newMetadata = {}
        missingKeys = []
        reviewable = False
        if stakeholders[1] is not None:
            stakeholders[1].mark_complete(get_mandatory_keys(request, 'sh', True))
            missingKeys = stakeholders[1]._missing_keys
            newMetadata = stakeholders[1].get_metadata(request)
            
            reviewable = (len(missingKeys) == 0 and 
                'reviewableMessage' in templateValues and
                templateValues['reviewableMessage'] is None)
            
        if output_format == 'review':
            pendingVersions = []
            if availableVersions is None:
                availableVersions = review._get_available_versions(Stakeholder, 
                    uid, review=output_format=='review')
            for v in sorted(availableVersions, key=lambda v:v.get('version')):
                if v.get('status') == 1:
                    pendingVersions.append(v.get('version'))
            templateValues['pendingVersions'] = pendingVersions
            
        templateValues.update({
            'identifier': uid,
            'refVersion': refVersion,
            'refMetadata': refMetadata,
            'newVersion': newVersion,
            'newMetadata': newMetadata,
            'missingKeys': missingKeys,
            'reviewable': reviewable,
            'recalculated': recalculated,
            'camefrom': camefrom,
            'profile': get_current_profile(request),
            'locale': get_current_locale(request)
        })
        
        if output_format == 'review':
            return render_to_response(
                getTemplatePath(request, 'stakeholders/review.mak'),
                templateValues,
                request
            )
        else:
            return render_to_response(
                getTemplatePath(request, 'stakeholders/compare.mak'),
                templateValues,
                request
            )
    elif output_format == 'history':
        isLoggedIn, isModerator = checkUserPrivileges(request)
        stakeholders, count = stakeholder_protocol3.read_one_history(
            request, uid=uid)
        activeVersion = None
        for sh in stakeholders:
            if 'statusName' in sh:
                sh['statusName'] = get_translated_status(request, sh['statusName'])
            if sh.get('statusId') == 2:
                activeVersion = sh.get('version')
        
        templateValues = {
            'versions': stakeholders,
            'count': count,
            'activeVersion': activeVersion,
            'isModerator': isModerator
        }
        templateValues.update({
            'profile': get_current_profile(request),
            'locale': get_current_locale(request)
        })
        return render_to_response(
            getTemplatePath(request, 'stakeholders/history.mak'), 
            templateValues, request)
    elif output_format == 'formtest':
        # Test if a Stakeholder is valid according to the form configuration
        stakeholders = stakeholder_protocol3.read_one(request, uid=uid,
            public=False, translate=False)
        version = request.params.get('v', None)
        if (stakeholders and 'data' in stakeholders
            and len(stakeholders['data']) != 0):
            for sh in stakeholders['data']:
                if 'version' in sh:
                    if version is None:
                        version = str(sh['version'])
                    if str(sh['version']) == version:
                        categorylist = getCategoryList(request, 'stakeholders')
                        return render_to_response('json',
                            checkValidItemjson(categorylist, sh), request)
        return HTTPNotFound()
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

@view_config(route_name='stakeholders_read_one_public')
def read_one_public(request):
    """
    Read one Stakeholder based on ID and return all versions of this
    Stakeholder. Do not return any pending versions.
    Default output format: JSON
    """

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'json'

    uid = request.matchdict.get('uid', None)
    if check_valid_uuid(uid) is not True:
        raise HTTPNotFound()

    if output_format == 'json':
        stakeholders = stakeholder_protocol3.read_one(request, uid=uid,
            public=True)
        return render_to_response('json', stakeholders, request)
    elif output_format == 'html':
        #@TODO
        return render_to_response('json', {'HTML': 'Coming soon'}, request)
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()

@view_config(route_name='stakeholders_review', renderer='json')
def review(request):
    """
    Insert a review decision for a pending Stakeholder
    """

    _ = request.translate

    # Check if the user is logged in and he/she has sufficient user rights
    userid = authenticated_userid(request)
    if userid is None:
        raise HTTPUnauthorized(_('User is not logged in.'))
    if not isinstance(has_permission('moderate', request.context, request),
        ACLAllowed):
        raise HTTPUnauthorized(_('User has no permissions to add a review.'))
    user = Session.query(User).\
            filter(User.username == authenticated_userid(request)).first()

    # Query new version of Stakeholder
    stakeholder = Session.query(Stakeholder).\
        filter(Stakeholder.stakeholder_identifier == request.POST['identifier']).\
        filter(Stakeholder.version == request.POST['version']).\
        first()
    if stakeholder is None:
        raise HTTPUnauthorized(_('The Stakeholder was not found'))

    # If review decision is 'approved', make sure that all mandatory fields are
    # there, except if it is to be deleted
    review_decision = request.POST['review_decision']
    if review_decision == 'approve':
        review_decision = 1
    elif review_decision == 'reject':
        review_decision = 2
    else:
        raise HTTPBadRequest(_('No valid review decision'))
    
    review_comment = request.POST['review_comment']
    camefrom = request.POST['camefrom']

    if review_decision == 1: # Approved
        # Only check for mandatory keys if new version is not to be deleted
        # (has no tag groups)
        if len(stakeholder.tag_groups) > 0:
            mandatory_keys = get_mandatory_keys(request, 'sh')
            # Query keys
            stakeholder_keys = Session.query(SH_Key.key).\
                join(SH_Tag).\
                join(SH_Tag_Group, SH_Tag.fk_tag_group == SH_Tag_Group.id).\
                filter(SH_Tag_Group.stakeholder == stakeholder)
            keys = []
            for k in stakeholder_keys.all():
                keys.append(k.key)
            for mk in mandatory_keys:
                if mk not in keys:
                    raise HTTPBadRequest(_('Not all mandatory keys are provided'))

    # The user can add a review
    ret = stakeholder_protocol3._add_review(request, stakeholder, Stakeholder, 
        user, review_decision, review_comment)

    if 'success' not in ret:
        raise HTTPBadRequest(_('Unknown error'))
    
    if ret['success'] is True:
        request.session.flash(ret['msg'], 'success')
    else:
        request.session.flash(ret['msg'], 'error')
    
    if camefrom != '':
        camefromMsg = render(
            getTemplatePath(request, 'parts/messages/stakeholder_reviewed_through_involvement.mak'),
            {'url': request.route_url('activities_read_one', output='review', uid=camefrom)},
            request
        )
        request.session.flash(camefromMsg)

    return HTTPFound(location=request.route_url('stakeholders_read_one',
        output='history', uid=stakeholder.identifier))

@view_config(route_name='stakeholders_create', renderer='json')
def create(request):
    """
    Add a new stakeholder.
    Implements the create functionality (HTTP POST) in the CRUD model

    Test the POST request e.g. with
    curl --data @line.json http://localhost:6543/stakeholders

    """

    _ = request.translate

    # Check if the user is logged in and he/she has sufficient user rights
    userid = authenticated_userid(request)

    if userid is None:
        raise HTTPForbidden()
    if not isinstance(has_permission('edit', request.context, request),
        ACLAllowed):
        raise HTTPForbidden()

    ids = stakeholder_protocol3.create(request)

    # TODO: Do we still need translations here? Who is using this function
    # (since it is not Ext anymore)?

    response = {}

    if ids is not None:
        response['data'] = [i.to_json() for i in ids]
        response['total'] = len(response['data'])
        response['created'] = True
        response['msg'] = 'The Stakeholder was successfully created.'
        request.response.status = 201
    else:
        response['created'] = False
        response['msg'] = 'No Stakeholder was created.'
        request.response.status = 200

    return response
