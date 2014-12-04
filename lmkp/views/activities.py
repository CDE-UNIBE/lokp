import json
import logging
import urllib
from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPForbidden,
    HTTPFound,
    HTTPInternalServerError,
    HTTPNotFound,
    HTTPUnauthorized,
)
from pyramid.i18n import (
    get_localizer,
)
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
    A_Key,
    A_Tag,
    A_Tag_Group,
    Activity,
    Language,
)
from lmkp.models.meta import DBSession as Session
from lmkp.protocols.activity_protocol import ActivityProtocol
from lmkp.utils import (
    validate_uuid,
    handle_query_string,
    shorten_uuid,
)
from lmkp.views.activity_protocol3 import ActivityProtocol3
from lmkp.views.activity_review import ActivityReview
from lmkp.views.comments import comments_sitekey
from lmkp.views.config import get_mandatory_keys
from lmkp.views.download import DownloadView
from lmkp.views.form import (
    renderForm,
    renderReadonlyForm,
    renderReadonlyCompareForm,
    checkValidItemjson,
)
from lmkp.views.form_config import getCategoryList
from lmkp.views.profile import get_spatial_accuracy_map
from lmkp.views.translation import (
    get_translated_status,
    get_translated_db_keys,
)
from lmkp.views.views import (
    BaseView,
    get_bbox_parameters,
    get_output_format,
    get_page_parameters,
    get_status_parameter,
)

log = logging.getLogger(__name__)
activity_protocol = ActivityProtocol3(Session)


class ActivityView(BaseView):
    """
    This is the main class for viewing :term:`Activities`.

    Inherits from:
        :class:`lmkp.views.views.BaseView`
    """

    @view_config(route_name='activities_read_many')
    def read_many(self, public=False):
        """
        Return many :term:`Activities`.

        .. seealso::
            :ref:`read-many`

        For each :term:`Activity`, only one version is visible, always
        the latest visible version to the current user. This means that
        logged in users can see their own pending versions and
        moderators of the current profile can see pending versions as
        well. If you don't want to show pending versions, consider using
        :class:`lmkp.views.activities.ActivityView.read_many_public`
        instead.

        By default, the :term:`Activities` are ordered with the
        :term:`Activity` having the most recent change being on top.

        Args:
            ``public`` (bool): A boolean indicating whether to return
            only versions visible to the public (eg. no pending) or not.

        Matchdict parameters:

            ``/activities/{output}``

            ``output`` (str): If the output format is not valid, a 404
            Response is returned.

            The following output formats are supported:

                ``json``: Return the :term:`Activities` as JSON.

                ``geojson``: Return the :term:`Activities` as GeoJSON.

                ``html``: Return the :term:`Activities` as HTML (eg. the
                `Grid View`)

                ``form``: Returns the form to create a new
                :term:`Activity`.

                ``download``: Returns the page to download
                :term:`Activities`.

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
        activity_protocol = ActivityProtocol(self.request)
        output_format = get_output_format(self.request)

        if output_format == 'json':

            items = activity_protocol.read_many(public_query=public)

            return render_to_response('json', items, self.request)

        elif output_format == 'geojson':

            items = activity_protocol.read_many_geojson(public_query=public)

            return render_to_response('json', items, self.request)

        elif output_format == 'html':

            page, page_size = get_page_parameters(self.request)
            items = activity_protocol.read_many(
                public_query=public, limit=page_size,
                offset=page_size * page - page_size)

            spatial_filter = 'profile' if get_bbox_parameters(
                self.request)[0] == 'profile' else 'map'
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
                    self.request, 'activities/grid.mak'),
                template_values, self.request)

        elif output_format == 'form':

            is_logged_in, __ = get_user_privileges(self.request)
            if not is_logged_in:
                raise HTTPForbidden()

            new_involvement = self.request.params.get('inv', None)
            template_values = renderForm(
                self.request, 'activities', inv=new_involvement)

            if isinstance(template_values, Response):
                return template_values

            template_values.update(self.get_base_template_values())
            template_values.update({
                'uid': '-',
                'version': 0
            })

            return render_to_response(
                get_customized_template_path(
                    self.request, 'activities/form.mak'),
                template_values, self.request)

        elif output_format == 'download':

            download_view = DownloadView(self.request)

            return download_view.download_customize('activities')

        else:
            raise HTTPNotFound()

    @view_config(route_name='activities_public_read_many')
    def read_many_public(self):
        """
        Return many :term:`Activities` which are visible to the public.

        .. seealso::
            :class:`lmkp.views.activities.ActivityView.read_many` for
            details on the request parameters.

        In contrary to
        :class:`lmkp.views.activities.ActivityView.read_many`, no
        pending versions are returned even if the user is logged in.

        Matchdict parameters:

            ``/activities/public/{output}``

            ``output`` (str): If the output format is not valid, a 404
            Response is returned.

            The following output formats are supported:

                ``json``: Return the :term:`Activities` as JSON.

                ``geojson``: Return the :term:`Activities` as GeoJSON.

                ``html``: Return the :term:`Activities` as HTML (eg. the
                `Grid View`)

        Returns:
            ``HTTPResponse``. Either a HTML or a JSON response.
        """
        output_format = get_output_format(self.request)

        if output_format in ['json', 'geojson', 'html']:

            return self.read_many(public=True)

        else:
            raise HTTPNotFound()

    @view_config(route_name='activities_bystakeholders')
    def by_stakeholders(self, public=False):
        """
        Return many :term:`Activities` based on :term:`Stakeholders`.

        Based on the :term:`UIDs` of one or many :term:`Stakeholders`,
        all :term:`Activities` in which the :term:`Stakeholder` is
        involved are returned.

        .. seealso::
            :ref:`read-many`

        For each :term:`Activity`, only one version is visible, always
        the latest visible version to the current user. This means that
        logged in users can see their own pending versions and
        moderators of the current profile can see pending versions as
        well. If you don't want to show pending versions, consider using
        :class:`lmkp.views.activities.ActivityView.by_stakeholder_public`
        instead.

        By default, the :term:`Activities` are ordered with the
        :term:`Activity` having the most recent change being on top.

        Args:
            ``public`` (bool): A boolean indicating whether to return
            only versions visible to the public (eg. pending) or not.

        Matchdict parameters:

            ``/activities/bystakeholders/{output}/{uids}``

            ``output`` (str): If the output format is not valid, a 404
            Response is returned.

            The following output formats are supported:

                ``json``: Return the :term:`Activities` as JSON.

                ``html``: Return the :term:`Activities` as HTML (eg. the
                `Grid View`)

            ``uids`` (str): A comma-separated list of
            :term:`Stakeholder` :term:`UIDs`.

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
        activity_protocol = ActivityProtocol(self.request)
        output_format = get_output_format(self.request)

        uids = self.request.matchdict.get('uids', '').split(',')

        # Remove any invalid UIDs
        for uid in uids:
            if validate_uuid(uid) is not True:
                uids.remove(uid)

        if len(uids) == 0:
            raise HTTPNotFound()

        if output_format == 'json':

            items = activity_protocol.read_many(
                other_identifiers=uids, public_query=public)

            return render_to_response('json', items, self.request)

        elif output_format == 'html':

            page, page_size = get_page_parameters(self.request)

            items = activity_protocol.read_many(
                other_identifiers=uids, public_query=public, limit=page_size,
                offset=page_size * page - page_size)

            # No spatial filter is used if the Activities are filtered
            # by a Stakeholder
            spatial_filter = None
            status_filter = None

            template_values = self.get_base_template_values()
            template_values.update({
                'data': items['data'] if 'data' in items else [],
                'total': items['total'] if 'total' in items else 0,
                'spatialfilter': spatial_filter,
                'invfilter': uids,
                'statusfilter': status_filter,
                'currentpage': page,
                'pagesize': page_size,
                'handle_query_string': handle_query_string
            })

            return render_to_response(
                get_customized_template_path(
                    self.request, 'activities/grid.mak'),
                template_values, self.request)

        else:
            raise HTTPNotFound()

    @view_config(route_name='activities_bystakeholders_public')
    def by_stakeholders_public(self):
        """
        Return many :term:`Activities` based on :term:`Stakeholders`.

        Based on the :term:`UIDs` of one or many :term:`Stakeholders`,
        all :term:`Activities` in which the :term:`Stakeholder` is
        involved are returned.

        .. seealso::
            :class:`lmkp.views.activities.ActivityView.by_stakeholders`
            for more details on the request parameters.

        In contrary to
        :class:`lmkp.views.activities.ActivityView.by_stakeholders`, no
        pending versions are returned even if the user is logged in.

            Matchdict parameters:

            ``/activities/bystakeholders/public/{output}/{uids}``

            ``output`` (str): If the output format is not valid, a 404
            Response is returned.

            The following output formats are supported:

                ``json``: Return the :term:`Activities` as JSON.

                ``html``: Return the :term:`Activities` as HTML (eg. the
                `Grid View`)

            ``uids`` (str): A comma-separated list of
            :term:`Stakeholder` :term:`UIDs`.

        Returns:
            ``HTTPResponse``. Either a HTML or a JSON response.
        """
        output_format = get_output_format(self.request)

        if output_format in ['json', 'html']:

            return self.by_stakeholders(public=True)

        else:
            raise HTTPNotFound()

    @view_config(route_name='activities_read_one')
    def read_one(self, public=False):
        """
        Return one :term:`Activity`.

        .. seealso::
            :ref:`read-one`

        Read one :term:`Activity` or one version of an :term:`Activity`.
        By default, this is the latest visible version to the current
        user. This means that logged in users can see their own pending
        version and moderators of the current profile can see a pending
        version as well. If you don't want to see a version pending,
        consider using
        :class:`lmkp.views.activities.ActivityView.read_one_public`
        instead.

        Args:
            ``public`` (bool): A boolean indicating to return only a
            version visible to the public (eg. pending) or not.

        Matchdict parameters:

            ``/activities/{output}/{uid}``

            ``output`` (str): If the output format is not valid, a 404
            Response is returned.

            The following output formats are supported:

                ``json``: Return the :term:`Activity` as JSON. All
                versions visible to the current user are returned.

                ``geojson``: Return the :term:`Activity` as GeoJSON. A
                version parameter is required.

                ``html``: Return the :term:`Activity` as HTML (eg. the
                `Detail View`).

                ``form``: Returns the form to edit an existing
                :term:`Activity`.

                ``compare``: Return the page to compare two versions of
                the :term:`Activity`.

                ``review``: Return the page to review a pending version
                of an :term:`Activity`.

                ``statistics``: Return a page with the areal statistics
                of an :term:`Activity`.

            ``uid`` (str): An :term:`Activity` :term:`UID`.

        Request parameters:
            ``translate`` (bool): Return translated values or not. This
            is only valid for the output formats ``json`` or
            ``geojson``.

            ``v`` (int): Indicate a specific version to return. This is
            only valid for the output formats ``geojson``, ``html`` and
            ``form``.

            ``inv`` (str): Only valid for output format ``form``.
            Indicate an involvement of the form to return to after
            creating a new :term:`Stakeholder`.

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

            item = activity_protocol.read_one(
                self.request, uid=uid, public=public, translate=translate)

            return render_to_response('json', item, self.request)

        elif output_format == 'geojson':

            # A version is required
            version = self.request.params.get('v', None)
            if version is None:
                raise HTTPBadRequest(
                    'You must specify a version as parameter ?v=X')

            translate = self.request.params.get(
                'translate', 'true').lower() == 'true'

            item = activity_protocol.read_one_geojson_by_version(
                self.request, uid, version, translate=translate)

            return render_to_response('json', item, self.request)

        elif output_format == 'html':

            version = self.request.params.get('v', None)

            item = activity_protocol.read_one(
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
                        self.request, 'activities', i))
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
                            self.request, 'activities/details.mak'),
                        template_values, self.request)

            return HTTPNotFound()

        elif output_format == 'form':

            is_logged_in, __ = get_user_privileges(self.request)
            if not is_logged_in:
                raise HTTPForbidden()

            version = self.request.params.get('v', None)

            item = activity_protocol.read_one(
                self.request, uid=uid, public=False, translate=False)

            for i in item.get('data', []):

                item_version = i.get('version')
                if version is None:
                    # If there was no version provided, show the first
                    # version visible to the user
                    version = str(item_version)

                if str(item_version) == version:

                    new_involvement = self.request.params.get('inv')

                    template_values = renderForm(
                        self.request, 'activities', itemJson=i,
                        inv=new_involvement)
                    if isinstance(template_values, Response):
                        return template_values

                    template_values.update(self.get_base_template_values())
                    template_values.update({
                        'uid': uid,
                        'version': version
                    })

                    return render_to_response(
                        get_customized_template_path(
                            self.request, 'activities/form.mak'),
                        template_values, self.request)

            return HTTPNotFound()

        elif output_format in ['review', 'compare']:

            if output_format == 'review':
                # Only moderators can see the review page.
                is_logged_in, is_moderator = get_user_privileges(self.request)
                if not is_logged_in or not is_moderator:
                    raise HTTPForbidden()

            review = ActivityReview(self.request)
            is_review = output_format == 'review'
            available_versions = review._get_available_versions(
                Activity, uid, review=is_review)
            recalculated = False
            default_ref_version, default_new_version = review.\
                _get_valid_versions(Activity, uid)

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

            # If no valid new version is provided, use the default new version.
            if new_version is None or new_version not in [
                    v.get('version') for v in available_versions]:
                new_version = default_new_version

            if output_format == 'review':
                # If the Items are to be reviewed, only the changes which were
                # applied to the new_version are of interest
                items, recalculated = review.get_comparison(
                    Activity, uid, ref_version, new_version)
            else:
                # If the Items are to be compared, the versions as they are
                # stored in the database are of interest, without any
                # recalculation
                items = [
                    activity_protocol.read_one_by_version(
                        self.request, uid, ref_version, geometry='full',
                        translate=False),
                    activity_protocol.read_one_by_version(
                        self.request, uid, new_version, geometry='full',
                        translate=False)
                ]

            template_values = renderReadonlyCompareForm(
                self.request, 'activities', items[0], items[1],
                review=is_review)

            # Collect the metadata
            ref_metadata = {}
            new_metadata = {}
            missing_keys = []
            reviewable = False
            if items[0] is not None:
                ref_metadata = items[0].get_metadata(self.request)
            if items[1] is not None:
                new_metadata = items[1].get_metadata(self.request)

                items[1].mark_complete(get_mandatory_keys(
                    self.request, 'a', False))
                missing_keys = items[1]._missing_keys
                localizer = get_localizer(self.request)
                if localizer.locale_name != 'en':
                    db_lang = Session.query(Language).filter(
                        Language.locale == localizer.locale_name).first()
                    missing_keys = get_translated_db_keys(
                        A_Key, missing_keys, db_lang)
                    missing_keys = [m[1] for m in missing_keys]

                reviewable = (len(missing_keys) == 0 and
                              'reviewableMessage' in template_values and
                              template_values['reviewableMessage'] is None)

            if output_format == 'review':
                pending_versions = []
                for v in sorted(
                        available_versions, key=lambda v: v.get('version')):
                    if v.get('status') == 1:
                        pending_versions.append(v.get('version'))
                template_values.update({'pendingVersions': pending_versions})

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
            })

            if output_format == 'review':
                template = get_customized_template_path(
                    self.request, 'activities/review.mak')
            else:
                template = get_customized_template_path(
                    self.request, 'activities/compare.mak')

            return render_to_response(template, template_values, self.request)

        elif output_format == 'formtest':

            version = self.request.params.get('v', None)

            # Test if an Item is valid according to the form configuration
            items = activity_protocol.read_one(
                self.request, uid=uid, public=False, translate=False)

            for i in item.get('data', []):

                item_version = i.get('version')
                if version is None:
                    # If there was no version provided, show the first
                    # version visible to the user
                    version = str(item_version)

                if str(item_version) == version:

                    categorylist = getCategoryList(self.request, 'activities')
                    return render_to_response(
                        'json', checkValidItemjson(categorylist, i),
                        self.request)

            return HTTPNotFound()

        elif output_format == 'statistics':

            # Try to get the base URL to the web processing service which
            # provides the areal statistics.
            # If no web processing service is configured, it is assumed that
            # the platform does not provide the areal statistics
            try:
                wps_host = self.request.registry.settings['lmkp.base_wps']
            except KeyError:
                raise HTTPNotFound()

            # Check if the spatial accuracy map is configured in the
            # application .yml file
            spatial_accuracy_map = get_spatial_accuracy_map(self.request)
            if spatial_accuracy_map is None:
                raise HTTPNotFound()

            # Show the details of an Activity by rendering the form in readonly
            # mode.
            activities = activity_protocol.read_one(
                self.request, uid=uid, public=False, translate=False)

            activity = activities['data'][0]
            coords = activity['geometry']['coordinates']

            for taggroup in activity['taggroups']:
                if taggroup['main_tag']['key'] == "Spatial Accuracy":
                    spatial_accuracy = taggroup['main_tag']['value']

                    buffer = spatial_accuracy_map[spatial_accuracy]

            wps_parameters = {
                "ServiceProvider": "",
                "metapath": "",
                "Service": "WPS",
                "Request": "Execute",
                "Version": "1.0.0",
                "Identifier": "BufferStatistics",
                "DataInputs": "lon=%s;lat=%s;epsg=4326;buffer=%s" % (
                    coords[0], coords[1], buffer),
                "RawDataOutput": 'bufferstatistics@mimeType=application/json'
            }

            if not wps_host.endswith("?"):
                wps_host = "%s?" % wps_host
            for k, v in wps_parameters.items():
                wps_host = "%s%s=%s&" % (wps_host, k, v)

            log.debug("Accessing: %s" % wps_host)

            try:
                handle = urllib.urlopen(wps_host)
            except IOError:
                return HTTPInternalServerError("Remote server not accessible.")
            templateValues = json.loads(handle.read())
            templateValues['uid'] = uid
            templateValues['shortuid'] = uid.split("-")[0]
            return render_to_response(
                get_customized_template_path(
                    self.request, 'activities/statistics.mak'),
                templateValues, self.request)
        else:
            raise HTTPNotFound()

    @view_config(route_name='activities_read_one_public')
    def read_one_public(self):
        """
        Return one :term:`Activity`.

        .. seealso::
            :class:`lmkp.views.activities.ActivityView.read_one` for
            details on the request parameters.

        In contrary to
        :class:`lmkp.views.activities.ActivityView.read_one`, no
        pending versions are returned even if the user is logged in.

        Matchdict parameters:

            ``/activities/public/{output}/{uid}``

            ``output`` (str): If the output format is not valid, a 404
            Response is returned.

            The following output formats are supported:

                ``json``: Return the :term:`Activity` as JSON. All
                versions visible to the current user are returned.

                ``html``: Return the :term:`Activity` as HTML (eg. the
                `Detail View`).

            ``uid`` (str): An :term:`Activity` :term:`UID`.

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

    @view_config(route_name='activities_read_one_active')
    def read_one_active(self):
        """
        Return one active :term:`Activity`.

        .. seealso::
            :ref:`read-one`

        Read one active :term:`Activity` version. Only return the active
        version. If there is no active version, no version is returned.

        Matchdict parameters:

            ``/activities/active/{output}/{uid}``

            ``output`` (str): If the output format is not valid, a 404
            Response is returned.

            The following output formats are supported:

                ``json``: Return the :term:`Activity` as JSON. All
                versions visible to the current user are returned.

            ``uid`` (str): An :term:`Activity` :term:`UID`.

        Returns:
            ``HTTPResponse``. Either a HTML or a JSON response.
        """
        output_format = get_output_format(self.request)

        uid = self.request.matchdict.get('uid', None)
        if validate_uuid(uid) is not True:
            raise HTTPNotFound()

        if output_format == 'json':

            item = activity_protocol.read_one_active(self.request, uid=uid)

            return render_to_response('json', item, self.request)

        else:
            raise HTTPNotFound()

    @view_config(route_name='activities_read_one_history')
    def history(self):
        """
        Return the history of an :term:`Activity`.

        Logged in users can see their own pending versions and
        moderators of the current profile can see pending versions as
        well.

        By default, the versions are ordered with the most recent
        changes being on top.

        Matchdict parameters:

            ``/activities/history/{output}/{uid}``

            ``output`` (str): If the output format is not valid, a 404
            Response is returned.

            The following output formats are supported:

                ``html``: Return the history view as HTML.

                ``rss``: Return history view as RSS feed.

            ``uid`` (str): An :term:`Activity` :term:`UID`.

        Returns:
            ``HTTPResponse``. Either a HTML or a JSON response.
        """
        output_format = get_output_format(self.request)

        uid = self.request.matchdict.get('uid', None)
        if validate_uuid(uid) is not True:
            raise HTTPNotFound()

        __, is_moderator = get_user_privileges(self.request)
        items, count = activity_protocol.read_one_history(
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
                self.request, 'activities/history.mak')

        elif output_format == 'rss':
            template = get_customized_template_path(
                self.request, 'activities/history_rss.mak')

        else:
            raise HTTPNotFound()

        return render_to_response(template, template_values, self.request)

    @view_config(route_name='activities_review', renderer='json')
    def review(self):
        """
        Review a pending :term:`Activity` version.

        A review can only be done by moderators and if the
        :term:`Activity` is situated within one of the profiles of the
        moderator.

        POST parameters:

            ``identifier`` (str): An :term:`Activity` :term:`UID`.

            ``version`` (int): The version of the :term:`Activity` to be
            reviewed

            ``review_decision`` (str): One of ``approve`` or ``reject``.

            ``review_comment`` (str): An optional comment to be stored
            with the review.

        Returns:
            ``HTTPResponse``. If the review was successful, the history
            page of the :term:`Activity` is returned.
        """
        is_logged_in, is_moderator = get_user_privileges(self.request)
        if not is_logged_in:
            raise HTTPUnauthorized('User is not logged in.')
        if not is_moderator:
            raise HTTPUnauthorized(
                'User has no permissions to add a review.')

        profile_filters = activity_protocol._get_spatial_moderator_filter(
            self.request)
        if profile_filters is None:
            raise HTTPBadRequest('User has no profile attached')

        activity = Session.query(Activity).\
            filter(
                Activity.activity_identifier == self.request.POST[
                    'identifier']).\
            filter(Activity.version == self.request.POST['version']).\
            filter(profile_filters).\
            first()
        if activity is None:
            raise HTTPUnauthorized(
                "The Item was not found or is not situated within the user's "
                "profiles")

        review_decision = self.request.POST['review_decision']
        if review_decision == 'approve':
            review_decision = 1
        elif review_decision == 'reject':
            review_decision = 2
        else:
            raise HTTPBadRequest('No valid review decision')

        # Only check for mandatory keys if the new version is to be approved
        # and if it is not to be deleted (in which case it has no tag groups)
        if review_decision == 1 and len(activity.tag_groups) > 0:
            mandatory_keys = get_mandatory_keys(self.request, 'a')
            activity_keys = Session.query(A_Key.key).\
                join(A_Tag).\
                join(A_Tag_Group, A_Tag.fk_tag_group == A_Tag_Group.id).\
                filter(A_Tag_Group.activity == activity)
            keys = []
            for k in activity_keys.all():
                keys.append(k.key)
            for mk in mandatory_keys:
                if mk not in keys:
                    raise HTTPBadRequest(
                        'Not all mandatory keys are provided')

        review = activity_protocol._add_review(
            self.request, activity, Activity, self.request.user,
            review_decision, self.request.POST.get('review_comment', ''))

        review_success = review.get('success', False)
        if review_success:
            self.request.session.flash(review.get('msg'), 'success')
        else:
            if review.get('msg') is None:
                raise HTTPBadRequest('Unknown error')
            self.request.session.flash(review.get('msg'), 'error')

        return HTTPFound(location=self.request.route_url(
            'activities_read_one_history', output='html',
            uid=activity.identifier))

    @view_config(route_name='activities_create', renderer='json')
    def create(self):
        """
        Create a new version of an :term:`Activity`.

        Only logged in users with edit privileges can create new
        versions.

        POST parameters:

            ``<body>`` The JSON body must contain the diff to create the
            new :term:`Activity`.

        Returns:
            ``HTTPResponse``. A Response with status code 201 indicates
            that the :term:`Activity` was successfully created. Status
            code 200 means that no version was created.
        """
        is_logged_in, __ = get_user_privileges(self.request)

        if not is_logged_in:
            raise HTTPForbidden()
        if not isinstance(has_permission(
                'edit', self.request.context, self.request), ACLAllowed):
            raise HTTPForbidden()

        ids = activity_protocol.create(self.request)

        response = {}
        if ids is not None:
            data = [i.to_json() for i in ids]
            response.update({
                'data': data,
                'total': len(data),
                'created': True,
                'msg': 'The Activity was successfully created.'
            })
            self.request.response.status = 201
        else:
            response.update({
                'created': False,
                'msg': 'No Activity was created.'
            })
            self.request.response.status = 200

        return response
