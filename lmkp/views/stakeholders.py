import logging
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPUnauthorized
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import TranslationStringFactory
from pyramid.i18n import get_localizer
from pyramid.renderers import render_to_response
from pyramid.renderers import render
from pyramid.response import Response
from pyramid.security import ACLAllowed
from pyramid.security import authenticated_userid
from pyramid.security import has_permission
from pyramid.view import view_config

from lmkp.authentication import get_user_privileges
from lmkp.custom import get_customized_template_path
from lmkp.models.database_objects import (
    Language,
    SH_Key,
    SH_Tag,
    SH_Tag_Group,
    Stakeholder,
    User,
)
from lmkp.models.meta import DBSession as Session
from lmkp.utils import (
    validate_uuid,
    handle_query_string
)
from lmkp.views.comments import comments_sitekey
from lmkp.views.config import get_mandatory_keys
from lmkp.views.download import DownloadView
from lmkp.views.form import (
    checkValidItemjson,
    renderForm,
    renderReadonlyCompareForm,
    renderReadonlyForm,
)
from lmkp.views.form_config import getCategoryList
from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
from lmkp.views.stakeholder_review import StakeholderReview
from lmkp.views.translation import (
    get_translated_status,
    get_translated_db_keys,
)
from lmkp.views.views import (
    BaseView,
    get_bbox_parameters,
    get_current_locale,
    get_current_profile,
    get_output_format,
    get_page_parameters,
    get_status_parameter,
)


log = logging.getLogger(__name__)
_ = TranslationStringFactory('lmkp')
stakeholder_protocol = StakeholderProtocol3(Session)


class StakeholderView(BaseView):
    """
    This is the main class for viewing :term:`Stakeholders`.

    Inherits from:
        :class:`lmkp.views.views.BaseView`
    """

    @view_config(route_name='stakeholders_read_many')
    def read_many(self, public=False):
        """
        Return many :term:`Stakeholders`.

        .. seealso::
            :ref:`read-many`

        For each :term:`Stakeholder`, only one version is visible,
        always the latest visible version to the current user. This
        means that logged in users can see their own pending versions
        and moderators of the current profile can see pending versions
        as well. If you don't want to show pending versions, consider
        using
        :class:`lmkp.views.stakeholders.StakeholderView.read_many_public`
        instead.

        By default, the :term:`Stakeholders` are ordered with the
        :term:`Stakeholder` having the most recent change being on top.

        Args:
            ``public`` (bool): A boolean indicating whether to return
            only versions visible to the public (eg. pending) or not.

        Matchdict parameters:

            ``/stakeholders/{output}``

            ``output`` (str): If the output format is not valid, a 404
            Response is returned.

            The following output formats are supported:

                ``json``: Return the :term:`Stakeholders` as JSON.

                ``html``: Return the :term:`Stakeholders` as HTML (eg.
                the `Grid View`)

                ``form``: Returns the form to create a new
                :term:`Stakeholder`.

                ``download``: Returns the page to download
                :term:`Stakeholders`.

        Request parameters:
            ``page`` (int): The page parameter is used to paginate
            :term:`Items`. In combination with ``pagesize`` it defines
            the offset.

            ``pagesize`` (int): The pagesize parameter defines how many
            :term:`Items` are displayed at once. It is used in
            combination with ``page`` to allow pagination.

            ``status`` (str): Use the status parameter to limit results
            to displaying only versions with a certain :term:`status`.

        Returns:
            ``HTTPResponse``. Either a HTML or a JSON response.
        """

        output_format = get_output_format(self.request)

        if output_format == 'json':

            items = stakeholder_protocol.read_many(self.request, public=False)

            return render_to_response('json', items, self.request)

        elif output_format == 'html':

            page, page_size = get_page_parameters(self.request)
            items = stakeholder_protocol.read_many(
                self.request, public=public, limit=page_size,
                offset=page_size * page - page_size)

            spatial_filter = None
            status_filter = get_status_parameter(self.request)
            __, is_moderator = get_user_privileges(self.request)

            template_values = self.get_base_template_values()
            template_values.update({
                'data': items['data'] if 'data' in items else [],
                'total': items['total'] if 'total' in items else 0,
                'spatialfilter': spatial_filter,
                'invfilter': None,
                'statusfilter': status_filter,
                'currentpage': page,
                'pagesize': page_size,
                'is_moderator': is_moderator,
                'handle_query_string': handle_query_string
            })

            return render_to_response(
                get_customized_template_path(
                    self.request, 'stakeholders/grid.mak'),
                template_values, self.request)

        elif output_format == 'form':

            is_logged_in, __ = get_user_privileges(self.request)
            if not is_logged_in:
                raise HTTPForbidden()

            new_involvement = self.request.params.get('inv', None)
            template_values = renderForm(
                self.request, 'stakeholders', inv=new_involvement)

            if isinstance(template_values, Response):
                return template_values

            template_values.update({
                'profile': get_current_profile(self.request),
                'locale': get_current_locale(self.request)
            })

            return render_to_response(
                get_customized_template_path(
                    self.request, 'stakeholders/form.mak'),
                template_values, self.request
            )

        elif output_format == 'download':

            download_view = DownloadView(self.request)

            return download_view.download_customize('stakeholders')

        else:
            raise HTTPNotFound()

    @view_config(route_name='stakeholders_read_many_public')
    def read_many_public(self):
        """
        Return many :term:`Stakeholders` which are visible to the
        public.

        .. seealso::
            :class:`lmkp.views.stakeholders.StakeholderView.read_many`
            for details on the request parameters.

        In contrary to
        :class:`lmkp.views.stakeholders.StakeholderView.read_many`, no
        pending versions are returned even if the user is logged in.

        Matchdict parameters:

            ``/stakeholders/public/{output}``

            ``output`` (str): If the output format is not valid, a 404
            Response is returned.

            The following output formats are supported:

                ``json``: Return the :term:`Stakeholders` as JSON.

                ``html``: Return the :term:`Stakeholders` as HTML (eg.
                the `Grid View`)

        Returns:
            ``HTTPResponse``. Either a HTML or a JSON response.
        """
        output_format = get_output_format(self.request)

        if output_format in ['json', 'html']:

            return self.read_many(public=True)

        else:
            raise HTTPNotFound()

    @view_config(route_name='stakeholders_byactivities')
    @view_config(route_name='stakeholders_byactivities_all')
    def by_activities(self, public=False):
        """
        Return many :term:`Stakeholders` based on :term:`Activities`.

        Based on the :term:`UIDs` of one or many :term:`Activities`,
        all :term:`Stakeholders` which are involved in the
        :term:`Activity` are returend.

        .. seealso::
            :ref:`read-many`

        For each :term:`Stakeholder`, only one version is visible,
        always the latest visible version to the current user. This
        means that logged in users can see their own pending versions
        and moderators of the current profile can see pending versions
        as well. If you don't want to show pending versions, consider
        using
        :class:`lmkp.views.stakeholders.StakeholderView.by_activities_public`
        instead.

        By default, the :term:`Stakeholders` are ordered with the
        :term:`Stakeholder` having the most recent change being on top.

        Args:
            ``public`` (bool): A boolean indicating whether to return
            only versions visible to the public (eg. pending) or not.

        Matchdict parameters:

            ``/stakeholders/byactivities/{output}`` or
            ``/stakeholders/byactivities/{output}/{uids}``

            ``output`` (str): If the output format is not valid, a 404
            Response is returned.

            The following output formats are supported:

                ``json``: Return the :term:`Stakeholders` as JSON.

                ``html``: Return the :term:`Stakeholders` as HTML (eg.
                the `Grid View`)

            ``uids`` (str): An optional comma-separated list of
            :term:`Activity` :term:`UIDs`.

        Request parameters:
            ``page`` (int): The page parameter is used to paginate
            :term:`Items`. In combination with ``pagesize`` it defines
            the offset.

            ``pagesize`` (int): The pagesize parameter defines how many
            :term:`Items` are displayed at once. It is used in
            combination with ``page`` to allow pagination.

            ``status`` (str): Use the status parameter to limit results
            to displaying only versions with a certain :term:`status`.

        Returns:
            ``HTTPResponse``. Either a HTML or a JSON response.
        """
        output_format = get_output_format(self.request)

        uids = self.request.matchdict.get('uids', '').split(',')

        # Remove any invalid UIDs
        for uid in uids:
            if validate_uuid(uid) is not True:
                uids.remove(uid)

        if output_format == 'json':

            items = stakeholder_protocol.read_many_by_activities(
                self.request, public=public, uids=uids)

            return render_to_response('json', items, self.request)

        elif output_format == 'html':

            page, page_size = get_page_parameters(self.request)

            items = stakeholder_protocol.read_many_by_activities(
                self.request, public=public, uids=uids, limit=page_size,
                offset=page_size * page - page_size)

            # Show a spatial filter only if there is no involvement
            # filter (no Activity UID set)
            spatial_filter = None
            if len(uids) == 0:
                spatial_filter = 'profile' if get_bbox_parameters(
                    self.request)[0] == 'profile' else 'map'
            status_filter = None

            __, is_moderator = get_user_privileges(self.request)

            template_values = self.get_base_template_values()
            template_values.update({
                'data': items['data'] if 'data' in items else [],
                'total': items['total'] if 'total' in items else 0,
                'spatialfilter': spatial_filter,
                'invfilter': uids,
                'statusfilter': status_filter,
                'currentpage': page,
                'pagesize': page_size,
                'is_moderator': is_moderator,
                'handle_query_string': handle_query_string
            })

            return render_to_response(
                get_customized_template_path(
                    self.request, 'stakeholders/grid.mak'),
                template_values, self.request)

        else:
            raise HTTPNotFound()

    @view_config(route_name='stakeholders_byactivities_public')
    @view_config(route_name='stakeholders_byactivities_all_public')
    def by_activities_public(self):
        """
        Return many :term:`Stakeholders` based on :term:`Activities`.

        Based on the :term:`UIDs` of one or many :term:`Activities`,
        all :term:`Stakeholders` which are involved in the
        :term:`Activity` are returend.

        .. seealso::
            :class:`lmkp.views.stakeholders.StakeholderView.by_activities`
            for more details on the request parameters.

        In contrary to
        :class:`lmkp.views.stakeholders.StakeholderView.by_activities`,
        no pending versions are returned even if the user is logged in.

        Matchdict parameters:

            ``/stakeholders/byactivities/public/{output}`` or
            ``/stakeholders/byactivities/public/{output}/{uids}``

            ``output`` (str): If the output format is not valid, a 404
            Response is returned.

            The following output formats are supported:

                ``json``: Return the :term:`Stakeholders` as JSON.

                ``html``: Return the :term:`Stakeholders` as HTML (eg.
                the `Grid View`)

            ``uids`` (str): An optional comma-separated list of
            :term:`Activity` :term:`UIDs`.

        Returns:
            ``HTTPResponse``. Either a HTML or a JSON response.
        """
        output_format = get_output_format(self.request)

        if output_format in ['json', 'html']:

            return self.by_activities(public=True)

        else:
            raise HTTPNotFound()


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
    if validate_uuid(uid) is not True:
        raise HTTPNotFound()

    if output_format == 'json':
        stakeholders = stakeholder_protocol.read_one_active(request, uid=uid)
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
    if validate_uuid(uid) is not True:
        raise HTTPNotFound()

    if output_format == 'json':
        stakeholders = stakeholder_protocol.read_one(
            request, uid=uid, public=True)
        return render_to_response('json', stakeholders, request)
    elif output_format == 'html':
        #@TODO
        return render_to_response('json', {'HTML': 'Coming soon'}, request)
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()


@view_config(
    route_name='stakeholders_read_many_pending', permission='moderate')
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
        stakeholders = stakeholder_protocol.read_many_pending(request)
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
    if validate_uuid(uid) is not True:
        raise HTTPNotFound()

    translate = request.params.get('translate', 'true') == 'true'

    if output_format == 'json':
        stakeholders = stakeholder_protocol.read_one(
            request, uid=uid, public=False, translate=translate)
        return render_to_response('json', stakeholders, request)
    elif output_format == 'html':
        # Show the details of a Stakeholder by rendering the form in readonly
        # mode.
        stakeholders = stakeholder_protocol.read_one(
            request, uid=uid, public=False, translate=False)
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
                        templateValues = renderReadonlyForm(
                            request, 'stakeholders', sh)
                        templateValues['profile'] = get_current_profile(
                            request)
                        templateValues['locale'] = get_current_locale(request)

                        # Append the short uid and the uid to the templates
                        # values
                        templateValues['uid'] = uid
                        templateValues['shortuid'] = uid.split("-")[0]
                        # Append also the site key from the commenting system
                        templateValues['site_key'] = comments_sitekey(
                            request)['site_key']
                        # and the url of the commenting system
                        templateValues['comments_url'] = request.registry.\
                            settings['lmkp.comments_url']

                        return render_to_response(
                            get_customized_template_path(
                                request, 'stakeholders/details.mak'),
                            templateValues,
                            request
                        )
        return HTTPNotFound()
    elif output_format == 'form':
        if request.user is None:
            # Make sure the user is logged in
            raise HTTPForbidden()
        # Query the Stakeholders with the given identifier
        stakeholders = stakeholder_protocol.read_one(
            request, uid=uid, public=False, translate=False)
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
                        templateValues = renderForm(
                            request, 'stakeholders', itemJson=sh)
                        if isinstance(templateValues, Response):
                            return templateValues
                        templateValues['profile'] = get_current_profile(
                            request)
                        templateValues['locale'] = get_current_locale(request)
                        return render_to_response(
                            get_customized_template_path(
                                request, 'stakeholders/form.mak'),
                            templateValues,
                            request
                        )
        return HTTPNotFound()
    elif output_format in ['review', 'compare']:
        if output_format == 'review':
            # Only moderators can see the review page.
            isLoggedIn, isModerator = get_user_privileges(request)
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
            except:
                refVersion = None
        if refVersion is None or output_format == 'review':
            # No reference version indicated, use the default one
            # Also use the default one for review because it cannot be changed.
            refVersion = defaultRefVersion
        else:
            availableVersions = review._get_available_versions(
                Stakeholder, uid, review=output_format == 'review')
            # Check if the indicated reference version is valid
            if refVersion not in [v.get('version') for v in availableVersions]:
                refVersion = defaultRefVersion

        newVersion = request.params.get('new', None)
        if newVersion is not None:
            try:
                newVersion = int(newVersion)
            except:
                newVersion = None
        if newVersion is None:
            # No new version indicated, use the default one
            newVersion = defaultNewVersion
        else:
            if availableVersions is None:
                availableVersions = review._get_available_versions(
                    Stakeholder, uid, review=output_format == 'review')
            # Check if the indicated new version is valid
            if newVersion not in [v.get('version') for v in availableVersions]:
                newVersion = defaultNewVersion

        if output_format == 'review':
            # If the Stakeholders are to be reviewed, only the changes which
            # were applied to the newVersion are of interest
            stakeholders, recalculated = review.get_comparison(
                Stakeholder, uid, refVersion, newVersion)
        else:
            # If the Stakeholders are compared, the versions as they are stored
            # in the database are of interest, without any recalculation
            stakeholders = [
                stakeholder_protocol.read_one_by_version(
                    request, uid, refVersion, translate=False
                ),
                stakeholder_protocol.read_one_by_version(
                    request, uid, newVersion, translate=False
                )
            ]
        templateValues = renderReadonlyCompareForm(
            request, 'stakeholders', stakeholders[0], stakeholders[1],
            review=output_format == 'review')
        # Collect metadata for the reference version
        refMetadata = {}
        if stakeholders[0] is not None:
            refMetadata = stakeholders[0].get_metadata(request)
        # Collect metadata and missing keys for the new version
        newMetadata = {}
        missingKeys = []
        reviewable = False
        if stakeholders[1] is not None:
            stakeholders[1].mark_complete(
                get_mandatory_keys(request, 'sh', False))
            missingKeys = stakeholders[1]._missing_keys
            localizer = get_localizer(request)
            if localizer.locale_name != 'en':
                db_lang = Session.query(Language).filter(
                    Language.locale == localizer.locale_name).first()
                missingKeys = get_translated_db_keys(
                    SH_Key, missingKeys, db_lang)
                missingKeys = [m[1] for m in missingKeys]
            newMetadata = stakeholders[1].get_metadata(request)

            reviewable = (
                len(missingKeys) == 0 and 'reviewableMessage' in templateValues
                and templateValues['reviewableMessage'] is None)

        if output_format == 'review':
            pendingVersions = []
            if availableVersions is None:
                availableVersions = review._get_available_versions(
                    Stakeholder, uid, review=output_format == 'review')
            for v in sorted(availableVersions, key=lambda v: v.get('version')):
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
                get_customized_template_path(
                    request, 'stakeholders/review.mak'),
                templateValues,
                request
            )
        else:
            return render_to_response(
                get_customized_template_path(
                    request, 'stakeholders/compare.mak'),
                templateValues,
                request
            )
    elif output_format == 'formtest':
        # Test if a Stakeholder is valid according to the form configuration
        stakeholders = stakeholder_protocol.read_one(
            request, uid=uid, public=False, translate=False)
        version = request.params.get('v', None)
        if (stakeholders and 'data' in stakeholders
                and len(stakeholders['data']) != 0):
            for sh in stakeholders['data']:
                if 'version' in sh:
                    if version is None:
                        version = str(sh['version'])
                    if str(sh['version']) == version:
                        categorylist = getCategoryList(request, 'stakeholders')
                        return render_to_response(
                            'json', checkValidItemjson(categorylist, sh),
                            request)
        return HTTPNotFound()
    else:
        # If the output format was not found, raise 404 error
        raise HTTPNotFound()


@view_config(route_name='stakeholders_read_one_history')
def read_one_history(request):
    # Handle the parameters (locale, profile)
    bv = BaseView(request)
    bv._handle_parameters()

    try:
        output_format = request.matchdict['output']
    except KeyError:
        output_format = 'html'

    uid = request.matchdict.get('uid', None)
    if validate_uuid(uid) is not True:
        raise HTTPNotFound()
    isLoggedIn, isModerator = get_user_privileges(request)
    stakeholders, count = stakeholder_protocol.read_one_history(
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

    if output_format == 'html':
        template = 'stakeholders/history.mak'

    # RSS feed output
    elif output_format == 'rss':
        template = 'stakeholders/history_rss.mak'

    else:
        raise HTTPNotFound("Requested output format is not supported.")

    return render_to_response(
        get_customized_template_path(request, template), templateValues,
        request)


@view_config(route_name='stakeholders_review', renderer='json')
def review(request):
    """
    Insert a review decision for a pending Stakeholder
    Required POST attributes:
    - identifier (string, uid)
    - version (int)
    - review_decision (string): approve / reject
    - review_comment (string): nullable
    - camefrom: uid of the Activity
    """

    _ = request.translate

    # Check if the user is logged in and he/she has sufficient user rights
    userid = authenticated_userid(request)
    if userid is None:
        raise HTTPUnauthorized(_('User is not logged in.'))
    if not isinstance(
            has_permission('moderate', request.context, request), ACLAllowed):
        raise HTTPUnauthorized(_('User has no permissions to add a review.'))
    user = Session.query(User).filter(
        User.username == authenticated_userid(request)).first()

    # Query new version of Stakeholder
    stakeholder = Session.query(Stakeholder).\
        filter(
            Stakeholder.stakeholder_identifier == request.POST['identifier']).\
        filter(Stakeholder.version == request.POST['version']).\
        first()
    if stakeholder is None:
        raise HTTPUnauthorized(_('The Item was not found'))

    # If review decision is 'approved', make sure that all mandatory fields are
    # there, except if it is to be deleted
    review_decision = request.POST['review_decision']
    if review_decision == 'approve':
        review_decision = 1
    elif review_decision == 'reject':
        review_decision = 2
    else:
        raise HTTPBadRequest(_('No valid review decision'))

    review_comment = request.POST.get('review_comment', '')
    camefrom = request.POST.get('camefrom', '')

    if review_decision == 1:  # Approved
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
                    raise HTTPBadRequest(_(
                        'Not all mandatory keys are provided'))

    # The user can add a review
    ret = stakeholder_protocol._add_review(
        request, stakeholder, Stakeholder, user, review_decision,
        review_comment)

    if 'success' not in ret or ret['success'] is False and 'msg' not in ret:
        raise HTTPBadRequest(_('Unknown error'))

    if ret['success'] is True:
        request.session.flash(ret['msg'], 'success')
    else:
        request.session.flash(ret['msg'], 'error')

    if camefrom != '':
        # Redirect back to moderation view of other
        return HTTPFound(request.route_url(
            'activities_read_one', output='review', uid=camefrom))

    return HTTPFound(location=request.route_url(
        'stakeholders_read_one_history', output='html',
        uid=stakeholder.identifier))


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

    if userid is None:
        raise HTTPForbidden()
    if not isinstance(has_permission(
            'edit', request.context, request), ACLAllowed):
        raise HTTPForbidden()

    ids = stakeholder_protocol.create(request)

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
