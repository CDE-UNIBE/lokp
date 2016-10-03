import logging
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPForbidden,
    HTTPFound,
    HTTPNotFound,
    HTTPUnauthorized,
)
from pyramid.i18n import get_localizer
from pyramid.renderers import render_to_response
from pyramid.response import Response
from pyramid.security import (
    ACLAllowed,
    has_permission,
)
from pyramid.view import view_config

from lmkp.authentication import get_user_privileges
from lmkp.custom import get_customized_template_path
from lmkp.models.database_objects import (
    Language,
    SH_Key,
    SH_Tag,
    SH_Tag_Group,
    Stakeholder,
)
from lmkp.models.meta import DBSession as Session
from lmkp.utils import (
    handle_query_string,
    shorten_uuid,
    validate_uuid,
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

            items = stakeholder_protocol.read_many(self.request, public=False, )

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

    @view_config(route_name='stakeholders_read_one')
    def read_one(self, public=False):
        """
        Return one :term:`Stakeholder`.

        .. seealso::
            :ref:`read-one`

        Read one :term:`Stakeholder` or one version of a
        :term:`Stakeholder`. By default, this is the latest visible
        version to the current user. This means that logged in users can
        see their own pending version and moderators of the current
        profile can see a pending version as well. If you don't want to
        see a version pending, consider using
        :class:`lmkp.views.stakeholders.StakeholderView.read_one_public`
        instead.

        Args:
            ``public`` (bool): A boolean indicating to return only a
            version visible to the public (eg. pending) or not.

        Matchdict parameters:

            ``/stakeholders/{output}/{uid}``

            ``output`` (str): If the output format is not valid, a 404
            Response is returned.

            The following output formats are supported:

                ``json``: Return the :term:`Stakeholder` as JSON. All
                versions visible to the current user are returned.

                ``html``: Return the :term:`Stakeholder` as HTML (eg.
                the `Detail View`).

                ``form``: Returns the form to edit an existing
                :term:`Stakeholder`.

                ``compare``: Return the page to compare two versions of
                the :term:`Stakeholder`.

                ``review``: Return the page to review a pending version
                of a :term:`Stakeholder`.

            ``uid`` (str): An :term:`Stakeholder` :term:`UID`.

        Request parameters:
            ``translate`` (bool): Return translated values or not. This
            is only valid for the output format ``json``.

            ``v`` (int): Indicate a specific version to return. This is
            only valid for the output formats ``html`` and ``form``.

            ``camefrom`` (uid): Only valid for output format ``review``.
            Indicate a :term:`Activity` to return to after reviewing the
            :term:`Stakeholder`.

            ``ref`` (int) and ``new`` (int): Indicate specific versions.
            This is only valid for the output formats ``compare`` and
            ``review``.

        Returns:
            ``HTTPResponse``. Either a HTML or a JSON response.
        """
        output_format = get_output_format(self.request)

        uid = self.request.matchdict.get('uid', None)
        if validate_uuid(uid) is not True:
            raise HTTPNotFound()

        if output_format == 'json':

            translate = self.request.params.get(
                'translate', 'true').lower() == 'true'

            item = stakeholder_protocol.read_one(
                self.request, uid=uid, public=public, translate=translate)

            return render_to_response('json', item, self.request)

        elif output_format == 'html':

            version = self.request.params.get('v', None)

            item = stakeholder_protocol.read_one(
                self.request, uid=uid, public=public, translate=False)

            for i in item.get('data', []):

                item_version = i.get('version')
                if version is None:
                    # If there was no version provided, show the first
                    # version visible to the user
                    version = str(item_version)

                if str(item_version) == version:

                    template_values = self.get_base_template_values()
                    template_values.update(renderReadonlyForm(
                        self.request, 'stakeholders', i))
                    template_values.update({
                        'uid': uid,
                        'shortuid': shorten_uuid(uid),
                        'version': version,
                        'site_key': comments_sitekey(self.request)['site_key'],
                        'comments_url': self.request.registry.settings[
                            'lmkp.comments_url']
                    })

                    return render_to_response(
                        get_customized_template_path(
                            self.request, 'stakeholders/details.mak'),
                        template_values, self.request)

            return HTTPNotFound()

        elif output_format == 'form':

            is_logged_in, __ = get_user_privileges(self.request)
            if not is_logged_in:
                raise HTTPForbidden()

            version = self.request.params.get('v', None)

            item = stakeholder_protocol.read_one(
                self.request, uid=uid, public=False, translate=False)

            for i in item.get('data', []):

                item_version = i.get('version')
                if version is None:
                    # If there was no version provided, show the first
                    # version visible to the user
                    version = str(item_version)

                if str(item_version) == version:

                    template_values = renderForm(
                        self.request, 'stakeholders', itemJson=i)
                    if isinstance(template_values, Response):
                        return template_values

                    template_values.update(self.get_base_template_values())

                    return render_to_response(
                        get_customized_template_path(
                            self.request, 'stakeholders/form.mak'),
                        template_values, self.request)

            return HTTPNotFound()

        elif output_format in ['review', 'compare']:

            if output_format == 'review':
                # Only moderators can see the review page.
                is_logged_in, is_moderator = get_user_privileges(self.request)
                if not is_logged_in or not is_moderator:
                    raise HTTPForbidden()

            review = StakeholderReview(self.request)
            is_review = output_format == 'review'
            available_versions = review._get_available_versions(
                Stakeholder, uid, review=is_review)
            recalculated = False
            default_ref_version, default_new_version = review.\
                _get_valid_versions(Stakeholder, uid)

            try:
                ref_version = int(self.request.params.get('ref'))
            except:
                ref_version = None

            # For review or if no valid reference version is provided, use the
            # default reference version.
            if (output_format == 'review' or ref_version is None
                    or ref_version not in [
                        v.get('version') for v in available_versions]):
                ref_version = default_ref_version

            try:
                new_version = int(self.request.params.get('new'))
            except:
                new_version = None

            if new_version is None or new_version not in [
                    v.get('version') for v in available_versions]:
                new_version = default_new_version

            if output_format == 'review':
                # If the Items are to be reviewed, only the changes which were
                # applied to the new_version are of interest
                items, recalculated = review.get_comparison(
                    Stakeholder, uid, ref_version, new_version)
            else:
                # If the Items are to be compared, the versions as they are
                # stored in the database are of interest, without any
                # recalculation
                items = [
                    stakeholder_protocol.read_one_by_version(
                        self.request, uid, ref_version, translate=False
                    ),
                    stakeholder_protocol.read_one_by_version(
                        self.request, uid, new_version, translate=False
                    )
                ]

            template_values = renderReadonlyCompareForm(
                self.request, 'stakeholders', items[0], items[1],
                review=is_review)

            # Collect the metadata
            ref_metadata = {}
            new_metadata = {}
            missing_keys = []
            reviewable = False
            if items[0] is not None:
                ref_metadata = items[0].get_metadata(self.request)
            # Collect metadata and missing keys for the new version
            if items[1] is not None:
                new_metadata = items[1].get_metadata(self.request)

                items[1].mark_complete(get_mandatory_keys(
                    self.request, 'sh', False))
                missing_keys = items[1]._missing_keys
                localizer = get_localizer(self.request)
                if localizer.locale_name != 'en':
                    db_lang = Session.query(Language).filter(
                        Language.locale == localizer.locale_name).first()
                    missing_keys = get_translated_db_keys(
                        SH_Key, missing_keys, db_lang)
                    missing_keys = [m[1] for m in missing_keys]

                reviewable = (len(missing_keys) == 0 and
                              'reviewableMessage' in template_values
                              and template_values['reviewableMessage'] is None)

            if output_format == 'review':
                pending_versions = []
                for v in sorted(
                        available_versions, key=lambda v: v.get('version')):
                    if v.get('status') == 1:
                        pending_versions.append(v.get('version'))
                template_values['pendingVersions'] = pending_versions

            template_values.update(self.get_base_template_values())
            template_values.update({
                'identifier': uid,
                'refVersion': ref_version,
                'refMetadata': ref_metadata,
                'newVersion': new_version,
                'newMetadata': new_metadata,
                'missingKeys': missing_keys,
                'reviewable': reviewable,
                'recalculated': recalculated,
                'camefrom': self.request.params.get('camefrom', ''),
            })

            if output_format == 'review':
                template = get_customized_template_path(
                    self.request, 'stakeholders/review.mak')
            else:
                template = get_customized_template_path(
                    self.request, 'stakeholders/compare.mak')

            return render_to_response(template, template_values, self.request)

        elif output_format == 'formtest':

            version = self.request.params.get('v', None)

            # Test if an Item is valid according to the form configuration
            items = stakeholder_protocol.read_one(
                self.request, uid=uid, public=False, translate=False)

            for i in item.get('data', []):

                item_version = i.get('version')
                if version is None:
                    # If there was no version provided, show the first
                    # version visible to the user
                    version = str(item_version)

                if str(item_version) == version:

                    categorylist = getCategoryList(
                        self.request, 'stakeholders')
                    return render_to_response(
                        'json', checkValidItemjson(categorylist, i),
                        self.request)

            return HTTPNotFound()

        else:
            raise HTTPNotFound()

    @view_config(route_name='stakeholders_read_one_public')
    def read_one_public(self):
        """
        Return one :term:`Stakeholder`.

        .. seealso::
            :class:`lmkp.views.stakeholders.StakeholderView.read_one`
            for details on the request parameters.

        In contrary to
        :class:`lmkp.views.stakeholders.StakeholderView.read_one`, no
        pending versions are returned even if the user is logged in.

        Matchdict parameters:

            ``/stakeholders/public/{output}/{uid}``

            ``output`` (str): If the output format is not valid, a 404
            Response is returned.

            The following output formats are supported:

                ``json``: Return the :term:`Stakeholder` as JSON. All
                versions visible to the current user are returned.

                ``html``: Return the :term:`Stakeholder` as HTML (eg. the
                `Detail View`).

            ``uid`` (str): A :term:`Stakeholder` :term:`UID`.

        Returns:
            ``HTTPResponse``. Either a HTML or a JSON response.
        """
        output_format = get_output_format(self.request)

        uid = self.request.matchdict.get('uid', None)
        if validate_uuid(uid) is not True:
            raise HTTPNotFound()

        if output_format in ['json', 'html']:

            return self.read_one(public=True)

        else:
            raise HTTPNotFound()

    @view_config(route_name='stakeholders_read_one_active')
    def read_one_active(self):
        """
        Return one active :term:`Stakeholder`.

        .. seealso::
            :ref:`read-one`

        Read one active :term:`Stakeholder` version. Only return the active
        version. If there is no active version, no version is returned.

        Matchdict parameters:

            ``/stakeholders/active/{output}/{uid}``

            ``output`` (str): If the output format is not valid, a 404
            Response is returned.

            The following output formats are supported:

                ``json``: Return the :term:`Stakeholder` as JSON. All
                versions visible to the current user are returned.

            ``uid`` (str): A :term:`Stakeholder` :term:`UID`.

        Returns:
            ``HTTPResponse``. Either a HTML or a JSON response.
        """
        output_format = get_output_format(self.request)

        uid = self.request.matchdict.get('uid', None)
        if validate_uuid(uid) is not True:
            raise HTTPNotFound()

        if output_format == 'json':

            item = stakeholder_protocol.read_one_active(self.request, uid=uid)

            return render_to_response('json', item, self.request)

        else:
            raise HTTPNotFound()

    @view_config(route_name='stakeholders_read_one_history')
    def history(self):
        """
        Return the history of an :term:`Stakeholder`.

        Logged in users can see their own pending versions and
        moderators of the current profile can see pending versions as
        well.

        By default, the versions are ordered with the most recent
        changes being on top.

        Matchdict parameters:

            ``/stakeholders/history/{output}/{uid}``

            ``output`` (str): If the output format is not valid, a 404
            Response is returned.

            The following output formats are supported:

                ``html``: Return the history view as HTML.

                ``rss``: Return history view as RSS feed.

            ``uid`` (str): A :term:`Stakeholder` :term:`UID`.

        Returns:
            ``HTTPResponse``. Either a HTML or a JSON response.
        """
        output_format = get_output_format(self.request)

        uid = self.request.matchdict.get('uid', None)
        if validate_uuid(uid) is not True:
            raise HTTPNotFound()

        __, is_moderator = get_user_privileges(self.request)
        items, count = stakeholder_protocol.read_one_history(
            self.request, uid=uid)

        active_version = None
        for i in items:
            if 'statusName' in i:
                i['statusName'] = get_translated_status(
                    self.request, i['statusName'])
            if i.get('statusId') == 2:
                active_version = i.get('version')

        template_values = self.get_base_template_values()

        template_values.update({
            'versions': items,
            'count': count,
            'activeVersion': active_version,
            'isModerator': is_moderator
        })

        if output_format == 'html':
            template = get_customized_template_path(
                self.request, 'stakeholders/history.mak')

        elif output_format == 'rss':
            template = get_customized_template_path(
                self.request, 'stakeholders/history_rss.mak')

        else:
            raise HTTPNotFound()

        return render_to_response(template, template_values, self.request)

    @view_config(route_name='stakeholders_review', renderer='json')
    def review(self):
        """
        Review a pending :term:`Stakeholder` version.

        A review can only be done by moderators.

        POST parameters:

            ``identifier`` (str): An :term:`Stakeholder` :term:`UID`.

            ``version`` (int): The version of the :term:`Stakeholder` to
            be reviewed

            ``review_decision`` (str): One of ``approve`` or ``reject``.

            ``review_comment`` (str): An optional comment to be stored
            with the review.

            ``camefrom`` (uid): An optional :term:`Activity` :term:`UID`
            to return back to after review.

        Returns:
            ``HTTPResponse``. If the review was successful, the history
            page of the :term:`Stakeholder` is returned.
        """
        is_logged_in, is_moderator = get_user_privileges(self.request)
        if not is_logged_in:
            raise HTTPUnauthorized('User is not logged in.')
        if not is_moderator:
            raise HTTPUnauthorized(
                'User has no permissions to add a review.')

        # Query new version of Stakeholder
        stakeholder = Session.query(Stakeholder).\
            filter(
                Stakeholder.stakeholder_identifier == self.request.POST[
                    'identifier']).\
            filter(Stakeholder.version == self.request.POST['version']).\
            first()
        if stakeholder is None:
            raise HTTPUnauthorized('The Item was not found')

        review_decision = self.request.POST['review_decision']
        if review_decision == 'approve':
            review_decision = 1
        elif review_decision == 'reject':
            review_decision = 2
        else:
            raise HTTPBadRequest('No valid review decision')

        # Only check for mandatory keys if the new version is to be approved
        # and if it is not to be deleted (in which case it has no tag groups)
        if review_decision == 1 and len(stakeholder.tag_groups) > 0:
            mandatory_keys = get_mandatory_keys(self.request, 'sh')
            stakeholder_keys = Session.query(SH_Key.key).\
                join(SH_Tag).\
                join(SH_Tag_Group, SH_Tag.fk_tag_group == SH_Tag_Group.id).\
                filter(SH_Tag_Group.stakeholder == stakeholder)
            keys = []
            for k in stakeholder_keys.all():
                keys.append(k.key)
            for mk in mandatory_keys:
                if mk not in keys:
                    raise HTTPBadRequest(
                        'Not all mandatory keys are provided')

        review = stakeholder_protocol._add_review(
            self.request, stakeholder, Stakeholder, self.request.user,
            review_decision, self.request.POST.get('review_comment', ''))

        review_success = review.get('success', False)
        if review_success:
            self.request.session.flash(review.get('msg'), 'success')
        else:
            if review.get('msg') is None:
                raise HTTPBadRequest('Unknown error')
            self.request.session.flash(review.get('msg'), 'error')

        # Redirect to moderation view of Activity if camefrom parameter is
        # available
        camefrom = self.request.POST.get('camefrom', '')
        if camefrom != '':
            return HTTPFound(self.request.route_url(
                'activities_read_one', output='review', uid=camefrom))

        return HTTPFound(location=self.request.route_url(
            'stakeholders_read_one_history', output='html',
            uid=stakeholder.identifier))

    @view_config(route_name='stakeholders_create', renderer='json')
    def create(self):
        """
        Create a new version of an :term:`Stakeholder`.

        Only logged in users with edit privileges can create new
        versions.

        POST parameters:

            ``<body>`` The JSON body must contain the diff to create the
            new :term:`Stakeholder`.

        Returns:
            ``HTTPResponse``. A Response with status code 201 indicates
            that the :term:`Stakeholder` was successfully created. Status
            code 200 means that no version was created.
        """
        is_logged_in, __ = get_user_privileges(self.request)

        if not is_logged_in:
            raise HTTPForbidden()
        if not isinstance(has_permission(
                'edit', self.request.context, self.request), ACLAllowed):
            raise HTTPForbidden()

        ids = stakeholder_protocol.create(self.request)

        response = {}
        if ids is not None:
            data = [i.to_json() for i in ids]
            response.update({
                'data': data,
                'total': len(data),
                'created': True,
                'msg': 'The Stakeholder was successfully created.'
            })
            self.request.response.status = 201
        else:
            response.update({
                'created': False,
                'msg': 'No Stakeholder was created.'
            })
            self.request.response.status = 200

        return response
