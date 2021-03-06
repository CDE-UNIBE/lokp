import json
import logging

import datetime
import uuid

import colander
import copy
from geoalchemy2 import functions as geofunctions, WKTElement
import geojson
from geoalchemy2.shape import from_shape
from pyramid.httpexceptions import HTTPBadRequest, HTTPNotFound
from pyramid.i18n import get_localizer
from pyramid.security import authenticated_userid, effective_principals
from shapely.geometry import Polygon, asShape
from sqlalchemy import distinct, desc, func, or_, not_, and_, cast, Float, asc, \
    select

from lokp.config.form import getCategoryList
from lokp.models import User, Changeset, Language, A_Key, Activity, A_Tag_Group, \
    Status, A_Tag, A_Value, Involvement, Stakeholder, Institution, \
    Stakeholder_Role, Profile
from lokp.protocols.protocol import Protocol, TagGroup, Tag, Inv, Feature
from lokp.utils.geometry import geometry_as_geojson
from lokp.views.translation import get_translated_db_keys, statusMap, \
    get_translated_status
from lokp.utils.views import get_bbox_parameters, validate_bbox, \
    get_current_profile

log = logging.getLogger(__name__)


class ActivityFeature(Feature):
    """
    Overwrites the super class Feature and adds the geometry property
    """

    def __init__(self, guid, order_value, geometry=None, version=None,
                 status=None, status_id=None, timestamp=None, diff_info=None,
                 ** kwargs):
        self._taggroups = []
        self._involvements = []
        self._guid = guid
        self._order_value = order_value
        self._geometry = geometry
        self._version = version
        self._status = status
        self._status_id = status_id
        self._timestamp = timestamp
        self._diff_info = diff_info

        self._previous_version = kwargs.pop('previous_version', None)

        self._user_privacy = kwargs.pop('user_privacy', None)
        self._user_id = kwargs.pop('user_id', None)
        self._user_name = kwargs.pop('user_name', None)
        self._user_firstname = kwargs.pop('user_firstname', None)
        self._user_lastname = kwargs.pop('user_lastname', None)

        self._institution_id = kwargs.pop('institution_id', None)
        self._institution_name = kwargs.pop('institution_name', None)
        self._institution_url = kwargs.pop('institution_url', None)
        self._institution_logo = kwargs.pop('institution_logo', None)

    def getMappedClass(self):
        return Activity

    def getOtherMappedClass(self):
        return Stakeholder

    def to_tags(self, request):
        """
        Return a short representation in tag form (array of keys/values) of the
        most important attributes of the feature (as defined in the yaml as
        'involvementoverview')
        """

        categoryList = getCategoryList(request, 'activities')
        overviewkeys = categoryList.getInvolvementOverviewKeyNames()
        overviewtags = [{'key': k[0], 'value': []} for k in overviewkeys]

        for rettag in overviewtags:
            for tg in self._taggroups:
                for t in tg.get_tags():
                    if t.get_key() == rettag['key']:
                        rettag['value'].append(t.get_value())
            rettag['value'] = ', '.join(rettag['value'])

        return overviewtags

    def get_geometry(self):
        return geometry_as_geojson(self._geometry)

    def to_table(self, request):
        """
        Returns a JSON compatible representation of this object
        """

        # Tag Groups
        tg = []
        for t in self._taggroups:
            tg.append(t.to_table())

        # Geometry
        geometry = geometry_as_geojson(self._geometry)

        ret = {
            'id': self._guid,
            'taggroups': tg
        }

        if geometry is not None:
            ret['geometry'] = geometry
        if self._version is not None:
            ret['version'] = self._version
        if self._status is not None and self._status in statusMap:
            ret['status'] = get_translated_status(request, self._status)
        if self._status_id is not None:
            ret['status_id'] = self._status_id
        if self._timestamp is not None:
            ret['timestamp'] = str(self._timestamp)

        if self._previous_version is not None:
            ret['previous_version'] = self._previous_version

        institution = {}
        if self._institution_id is not None:
            institution['id'] = self._institution_id
        if self._institution_name is not None:
            institution['name'] = self._institution_name
        if self._institution_url is not None:
            institution['url'] = self._institution_url
        if self._institution_logo is not None:
            institution['logo'] = self._institution_logo
        if institution != {}:
            ret['institution'] = institution

        user = {}
        if self._user_id is not None:
            user['id'] = self._user_id
        if self._user_name is not None:
            user['username'] = self._user_name
        # User details based on privacy settings
        if self._user_privacy is not None and self._user_privacy > 0:
            if self._user_firstname is not None:
                user['firstname'] = self._user_firstname
            if self._user_lastname is not None:
                user['lastname'] = self._user_lastname
        if user != {}:
            ret['user'] = user

        # Involvements
        if len(self._involvements) != 0:
            sh = []
            for i in self._involvements:
                sh.append(i.to_table(request))
            ret['involvements'] = sh

        return ret


class ActivityProtocol(Protocol):

    def __init__(self, Session):
        self.Session = Session
        # The following is a ConfigCategoryList object as in form_config.py
        self.categoryList = None

    def create(self, request, data=None):
        """
        Create or update Activities
        """

        diff = request.json_body if data is None else data

        user = self.Session.query(User). \
            filter(User.username == authenticated_userid(request)). \
            first()

        # Changeset
        changeset = Changeset()
        changeset.user = user

        # Check if the json body is a valid diff file
        if 'activities' not in diff:
            raise HTTPBadRequest(detail="Not a valid format")

        # Return the IDs of the newly created Activities
        ids = []
        # Also collect the diffs again because they may have changed (due to
        # recalculation)
        activity_diffs = []
        for activity in diff['activities']:

            # activity here is a dict of all taggroups submitted by the form.
            # Taggroups with polygon geometry are also included in this list,
            # even if they are empty (e.g. 'map1': {"geometry": colander.null})
            # which creates problems when saving taggroups and saving the
            # changeset (as colander.null cannot be dumped to JSON).
            # Remove these taggroups before continuing.
            category_list = getCategoryList(request, 'activities')

            cleaned_activity = copy.deepcopy(activity)
            cleaned_activity['taggroups'] = []

            for taggroup in activity.get('taggroups', []):
                main_tag_key = taggroup.get('main_tag', {}).get('key')
                _, _, config_taggroup = category_list.findCategoryThematicgroupTaggroupByMainkey(main_tag_key)

                # If the taggroup has a map and only contains a single tag with
                # an empty geometry, then move on
                tg_has_map = config_taggroup is not None and config_taggroup.getMap() is not None
                tg_has_single_tag = len(taggroup['tags']) == 1
                if config_taggroup is not None and tg_has_map and tg_has_single_tag:
                    tag = taggroup['tags'][0]
                    tag_value = tag.get('value')
                    if isinstance(tag_value, dict) and tag_value.get(
                            'geometry') == colander.null:
                        continue

                # Remove tags with empty geometry. Prevents errors when saving
                # taggroups having a main tag (e.g. intended area) but no
                # polygon was drawn.
                # But, do not remove tag with empty geometry if in the same
                # taggroup, a tag with geometry is to be removed. This means
                # that the geometry was deleted (1x "delete", 1x "add" with
                # empty geometry). In this case, leave the added empty geometry
                # so the geometry will be removed in the db.
                has_geometry_deleted = False
                for t in taggroup.get('tags', []):
                    t_has_geometry = isinstance(t['value'], dict) and \
                                      'geometry' in t['value']
                    if t_has_geometry and t['op'] == 'delete':
                        has_geometry_deleted = True

                tags = []
                for t in taggroup.get('tags', []):
                    v = t.get('value')
                    if v != {'geometry': colander.null}:
                        tags.append(t)
                    elif has_geometry_deleted:
                        t['value'] = {'geometry': None}
                        tags.append(t)
                taggroup['tags'] = tags

                cleaned_activity['taggroups'].append(taggroup)

            log.debug('The diff to create/update the activity after removing empty geometry taggroups: %s' % cleaned_activity)

            a, ret_diff = self._handle_activity(request, cleaned_activity, changeset)

            if a is not None:
                if ret_diff is not None:
                    # If a new diff came back, use this to replace the old one
                    cleaned_activity = ret_diff

                # Add the newly created identifier to the diff (this is
                # important if the item had no identifier before
                    try:
                        cleaned_activity[str('id')] = str(a.activity_identifier)
                    except(AttributeError):
                        cleaned_activity[str('id')] = str(a.fk_activity)  # TODO:

                ids.append(a)

                # Append the diffs
                activity_diffs.append(cleaned_activity)

        if len(ids) > 0:
            # At least one Activity was created
            changeset_diff = {'activities': activity_diffs}
            try:
                changeset.diff = json.dumps(changeset_diff)
            except TypeError:
                log.error(
                    'Changeset JSON Error with the following diff: %s'
                    % changeset_diff)
                return None

            return ids

        else:
            # No Activity was created
            return None

    def read_one_active(self, request, uid):

        relevant_activities = self._get_relevant_activities_one_active(uid)

        # Determine if and how detailed Involvements are to be displayed.
        # Default is: 'full'
        inv_details = request.params.get('involvements', 'full')

        query, count = self._query_many(request, relevant_activities,
                                        involvements=inv_details != 'none')

        activities = self._query_to_activities(
            request, query, involvements=inv_details, public_query=True)

        return {
            'total': count,
            'data': [a.to_table(request) for a in activities]
        }

    def read_all_keys(self, request):
        localizer = get_localizer(request)
        dbLang = self.Session.query(Language). \
            filter(Language.locale == localizer.locale_name). \
            first()
        query = self.Session.query(distinct(A_Key.key)).filter(
            A_Key.fk_language == dbLang.id).order_by(A_Key.key)
        return {
            'total': query.count(),
            'data': [k[0] for k in query.all()]
        }

    def read_one_by_version(self, request, uid, version, **kwargs):

        translate = kwargs.get('translate', True)

        relevant_activities = self._get_relevant_activities_one_by_version(
            uid, version)

        # Determine if and how detailed Involvements are to be displayed.
        # Default is: 'full'
        inv_details = request.params.get('involvements', 'full')

        query, count = self._query_many(
            request, relevant_activities, involvements=inv_details != 'none',
            metadata=True
        )

        fullGeometry = kwargs.get('geometry', False)
        if fullGeometry is False:
            fullGeometry = request.params.get('geometry', False)
        if fullGeometry is not False:
            fullGeometry = fullGeometry.lower() == 'full'

        activities = self._query_to_activities(
            request, query, involvements=inv_details, public_query=False,
            geom=fullGeometry, translate=translate
        )

        if len(activities) == 0:
            return None
        else:
            return activities[0]

    def read_one_history(self, request, uid):
        """
        Return the history of an Activity. Instead of querying all the
        attributes of the Feature, only some relevant information are collected
        and returned (as a dict, not as a feature!).
        """

        relevant_activities = self._get_relevant_activities_one(request, uid)

        limit = self._get_limit(request)
        offset = self._get_offset(request)

        query, count = self._query_history(
            relevant_activities, limit=limit, offset=offset)

        # Order the Activities by version
        query = query.order_by(desc(Activity.version))

        activities = self._query_to_history(query)

        return activities, count

    def read_one_geojson_by_version(
            self, request, uid, version, translate=True):
        """
        Return a GeoJSON representation of the geometry taggroups of an
        Activity version.
        """

        relevant_activities = self._get_relevant_activities_one_by_version(
            uid, version)

        query = self._query_taggroup_geojson(
            request, relevant_activities, translate=translate)

        return self._query_to_taggroup_geojson(query, translate=translate)

    ## TODO: this should return
    def read_one(self, request, uid, public=True, **kwargs):

        translate = kwargs.get('translate', True)

        relevant_activities = self._get_relevant_activities_one(
            request, uid, public_query=public)

        # Determine if and how detailed Involvements are to be displayed.
        # Default is: 'full'
        inv_details = request.params.get('involvements', 'full')

        # Get limit and offset from request.
        # Defaults: limit = None / offset = 0
        limit = self._get_limit(request)
        offset = self._get_offset(request)

        query, count = self._query_many(request, relevant_activities,
                                        limit=limit, offset=offset,
                                        involvements=inv_details != 'none',
                                        metadata=True)

        # Order the Activity by version
        query = query.order_by(desc(Activity.version))

        # Taggroup geometry ## TODO - insert geometry here? Queried activities don't contain geometry from database
        full_geometry = request.params.get('geometry', 'full')
        full_geometry = full_geometry.lower() == 'full'

        activities = self._query_to_activities(
            request, query, involvements=inv_details, public_query=public,
            geom=full_geometry, translate=translate
        )

        return {
            'total': count,
            'data': [a.to_table(request) for a in activities]
        }

    def read_many(self, request, public=True, **kwargs):
        """
        Valid kwargs:
        - limit
        - offset
        """

        relevant_activities = self._get_relevant_activities_many(
            request, public_query=public)

        # Determine if and how detailed Involvements are to be displayed.
        # Default is: 'full'
        inv_details = request.params.get('involvements', 'full')

        # Get limit and offset from request if they are not in kwargs.
        # Defaults: limit = None / offset = 0
        limit = kwargs.get('limit', self._get_limit(request))
        offset = kwargs.get('offset', self._get_offset(request))

        query, count = self._query_many(
            request, relevant_activities, limit=limit, offset=offset,
            involvements=inv_details != 'none')

        translate = kwargs.get('translate', True)
        activities = self._query_to_activities(
            request, query, involvements=inv_details, public_query=public,
            translate=translate)

        return {
            'total': count,
            'data': [a.to_table(request) for a in activities]
        }

    def read_many_by_stakeholders(self, request, uids, public=True, **kwargs):
        """
        Valid kwargs:
        - limit
        - offset
        """

        relevant_activities = self._get_relevant_activities_by_stakeholders(
            request, uids, public_query=public)

        # Determine if and how detailed Involvements are to be displayed.
        # Default is: 'full'
        inv_details = request.params.get('involvements', 'full')

        # Get limit and offset from request if they are not in kwargs.
        # Defaults: limit = None / offset = 0
        limit = kwargs.get('limit', self._get_limit(request))
        offset = kwargs.get('offset', self._get_offset(request))

        query, count = self._query_many(
            request, relevant_activities, limit=limit, offset=offset,
            involvements=inv_details != 'none')

        activities = self._query_to_activities(
            request, query, involvements=inv_details, public_query=public)

        return {
            'total': count,
            'data': [a.to_table(request) for a in activities]
        }

    def read_many_geojson(self, request, public=True):

        relevant_activities = self._get_relevant_activities_many(
            request, public_query=public, bbox_cookies=False)

        # Get limit and offset from request.
        # Defaults: limit = None / offset = 0
        limit = self._get_limit(request)
        offset = self._get_offset(request)

        # Get the additional attributes for the geojson query
        translate = request.params.get('translate', True)
        if translate is not True:
            translate = translate.lower() != 'false'
        queryAttrs = request.params.get('attrs', None)

        attrs = []
        dbLang = None
        if queryAttrs is not None:
            if translate is not False:
                localizer = get_localizer(request)
                dbLang = self.Session.query(Language). \
                    filter(Language.locale == localizer.locale_name). \
                    first()
                attrs = get_translated_db_keys(
                    A_Key, queryAttrs.split(','), dbLang)
            else:
                attrs = [(a, a) for a in queryAttrs.split(',')]

        # TG can only be used in combination with attrs=[]
        tggeom = request.params.get('tggeom', None)

        query = self._query_geojson(
            request, relevant_activities, limit=limit, offset=offset,
            attrs=attrs, tggeom=tggeom, dbLang=dbLang, translate=translate)

        return self._query_to_geojson(query, attrs, tggeom)

    def _get_relevant_activities_one_by_version(self, uid, version):
        # Create relevant Activities
        relevant_activities = self.Session.query(
            Activity.id.label('order_id'),
            func.char_length('').label('order_value'),
            Activity.fk_status,
            Activity.activity_identifier
        ). \
            outerjoin(A_Tag_Group). \
            filter(Activity.activity_identifier == uid). \
            filter(Activity.version == version). \
            group_by(Activity.id, Activity.fk_status,
                     Activity.activity_identifier, func.char_length(''))

        return relevant_activities

    def _get_relevant_activities_one_active(self, uid):

        # Create relevant Activities
        relevant_activities = self.Session.query(
            Activity.id.label('order_id'),
            func.char_length('').label('order_value'),
            Activity.fk_status,
            Activity.activity_identifier
        ). \
            outerjoin(A_Tag_Group). \
            filter(Activity.activity_identifier == uid). \
            filter(Activity.fk_status == 2). \
            group_by(Activity.id, Activity.fk_status,
                     Activity.activity_identifier, func.char_length(''))

        return relevant_activities

    def _get_relevant_activities_one(self, request, uid, public_query=False):
        """
        """

        logged_in, is_moderator = self._get_user_status(
            effective_principals(request))

        # Prepare dummy order query
        order_query = self.Session.query(
            Activity.id,
            func.char_length('').label('value')  # Dummy value
        ). \
            subquery()

        # Prepare status filter
        status_filter = self.Session.query(
            Status.id
        ). \
            filter(or_(* self._get_status_detail(request, public_query)))

        # Create relevant Activities
        relevant_activities = self.Session.query(
            Activity.id.label('order_id'),
            order_query.c.value.label('order_value'),
            Activity.fk_status,
            Activity.activity_identifier,
            Activity.version
        )

        # Filter by UID
        relevant_activities = relevant_activities. \
            filter(Activity.activity_identifier == uid)

        # Filter by version(s)
        versions = self._get_versions(request)
        if versions is not None:
            relevant_activities = relevant_activities. \
                filter(Activity.version.in_(versions))

        # Status filter
        relevant_activities = relevant_activities. \
            filter(Activity.fk_status.in_(status_filter))

        relevant_activities = relevant_activities. \
            outerjoin(A_Tag_Group). \
            outerjoin(order_query, order_query.c.id == Activity.id)

        # If logged in and it is not a public query, add pending versions by
        # current user to selection. This is not necessary for moderators
        # because they already see all pending versions (see * below)
        if logged_in and public_query is False and not is_moderator:

            request_user_id = (request.user.id if request.user is not None
            else None)

            pending_activities = self.Session.query(
                Activity.id.label('order_id'),
                order_query.c.value.label('order_value'),
                Activity.fk_status,
                Activity.activity_identifier,
                Activity.version
            )

            pending_activities = pending_activities. \
                join(Changeset). \
                filter(Activity.activity_identifier == uid). \
                filter(Activity.fk_status == 1). \
                filter(Changeset.fk_user == request_user_id)

            pending_activities = pending_activities. \
                outerjoin(A_Tag_Group). \
                outerjoin(order_query, order_query.c.id == Activity.id)

            relevant_activities = pending_activities.union(relevant_activities)

        if is_moderator:
            # * For moderators, it is important to filter out pending
            # Activities based on the spatial extent of the moderator's
            # profile. Otherwise, moderators could see pending Activities
            # in another profile.
            # However, we do want to keep them if they were created by the
            # moderator
            relevant_activities = relevant_activities. \
                filter(or_(
                not_(Activity.fk_status == 1),
                and_(
                    Activity.fk_status == 1,
                    self._get_spatial_moderator_filter(request)
                ),
                (Changeset.fk_user == request.user.id)
            ))

        # Join Activities with Tag Groups and order_query, then group it
        relevant_activities = relevant_activities. \
            group_by(Activity.id, Activity.fk_status,
                     Activity.activity_identifier, order_query.c.value,
                     Activity.version)

        return relevant_activities

    def _get_relevant_activities_dict(self, request, dicts):
        """
        ''dicts'': Dicts containing the identifier and the version of the
          Activities to query
        """

        # Prepare dicts
        dict_filter = []
        for d in dicts:
            dict_filter.append(and_(
                Activity.activity_identifier == d['identifier'],
                Activity.version == d['version']
            ))

        # Prepare order: Get the order from request
        order_query, order_numbers = self._get_order(
            request, Activity, A_Tag_Group, A_Tag, A_Key, A_Value)

        # Create relevant Activities
        relevant_activities = self.Session.query(
            Activity.id.label('order_id'),
            order_query.c.value.label('order_value'),
            Activity.fk_status,
            Activity.activity_identifier
        )

        # Dict filter
        relevant_activities = relevant_activities.filter(or_(*dict_filter))

        # Join Activities with Tag Groups and order_query, then group it
        relevant_activities = relevant_activities. \
            outerjoin(A_Tag_Group). \
            outerjoin(order_query, order_query.c.id == Activity.id). \
            group_by(Activity.id, order_query.c.value, Activity.fk_status,
                     Activity.activity_identifier)

        # Do the ordering
        if order_numbers is not None:
            if self._get_order_direction(request) == 'DESC':
                # Descending
                if order_numbers is True:
                    # Order by numbers: Cast values to float
                    relevant_activities = relevant_activities.order_by(
                        desc(cast(order_query.c.value, Float)))
                else:
                    # Order alphabetically
                    relevant_activities = relevant_activities.order_by(
                        desc(order_query.c.value))
            else:
                # Ascending
                if order_numbers is True:
                    # Order by numbers: Cast values to float
                    relevant_activities = relevant_activities.order_by(
                        asc(cast(order_query.c.value, Float)))
                else:
                    # Order alphabetically
                    relevant_activities = relevant_activities.order_by(
                        asc(order_query.c.value))

        return relevant_activities

    def _get_relevant_activities_many(
            self, request, filter=None, public_query=False, bbox_cookies=True):
        """
        ''filter'': An optional custom filter.
        ''public_query'': If set to true, no pending queries are made. Defaults
          to 'False'
        """
        logged_in, is_moderator = self._get_user_status(
            effective_principals(request))

        # Filter: If no custom filter was provided, get filters from request
        if filter is None:
            status_filter = self.Session.query(
                Status.id
            ). \
                filter(or_(* self._get_status(request)))
            (a_tag_filter, a_filter_length, sh_tag_filter, sh_filter_length
             ) = self._filter(request)
        else:
            status_filter = (filter['status_filter']
            if 'status_filter' in filter else None)
            a_tag_filter = (filter['a_tag_filter']
            if 'a_tag_filter' in filter else None)
            a_filter_length = (filter['a_filter_length']
            if 'a_filter_length' in filter else 0)
            sh_tag_filter = (filter['sh_tag_filter']
            if 'sh_tag_filter' in filter else None)
            sh_filter_length = (filter['sh_filter_length']
            if 'sh_filter_length' in filter else 0)

        # Prepare filter based on Activity attributes
        filter_subqueries = None
        if a_filter_length == 0:
            # If no filter is provided: pass
            pass
        elif self._get_logical_operator(request) == 'or':
            # OR
            all_subqueries = []
            for x in a_tag_filter:
                # Collect the Activity IDs for each filter
                taggroups_sq = x.subquery()
                single_subquery = self.Session.query(
                    Activity.id.label('a_filter_id')
                ). \
                    join(A_Tag_Group). \
                    join(taggroups_sq,
                         taggroups_sq.c.a_filter_tg_id == A_Tag_Group.id)
                all_subqueries.append(single_subquery)
            # Put all found Activity IDs together (UNION)
            filter_subqueries = all_subqueries[0]. \
                union(* all_subqueries[1:]). \
                subquery()
        else:
            # AND
            filter_subqueries = self.Session.query(
                Activity.id.label('a_filter_id')
            )
            for x in a_tag_filter:
                # Collect the Activity IDs for each filter
                taggroups_sq = x.subquery()
                single_subquery = self.Session.query(
                    Activity.id.label('a_filter_id')
                ). \
                    join(A_Tag_Group). \
                    join(taggroups_sq,
                         taggroups_sq.c.a_filter_tg_id == A_Tag_Group.id). \
                    subquery()
                # Join each found Activity ID with previously found IDs
                filter_subqueries = filter_subqueries. \
                    join(single_subquery,
                         single_subquery.c.a_filter_id == Activity.id)
            filter_subqueries = filter_subqueries.subquery()

        # Prepare order: Get the order from request
        order_query, order_numbers = self._get_order(
            request, Activity, A_Tag_Group, A_Tag, A_Key, A_Value)

        # Create relevant Activities
        relevant_activities = self.Session.query(
            Activity.id.label('order_id'),
            order_query.c.value.label('order_value'),
            Activity.fk_status,
            Activity.activity_identifier
        )

        # Add a status filter if there is one set
        if request.params.get('status', None) is not None:
            relevant_activities = relevant_activities. \
                filter(Activity.fk_status.in_(status_filter))

        # Join Activities with TagGroups
        if filter_subqueries is not None:
            # If a filter was provided, join with filtered subqueries
            relevant_activities = relevant_activities. \
                join(filter_subqueries,
                     filter_subqueries.c.a_filter_id == Activity.id)
        else:
            # If no filter was provided, simply join with A_Tag_Group (outer
            # join to also capture empty Items)
            relevant_activities = relevant_activities. \
                outerjoin(A_Tag_Group)

        # Always filter by profile boundary
        relevant_activities = relevant_activities. \
            filter(self._get_profile_filter(request))

        # Filter spatially
        bbox_filter = self._get_bbox_filter(request, cookies=bbox_cookies)
        if bbox_filter is not None:
            relevant_activities = relevant_activities.filter(bbox_filter)

        # Join Activities with order and group
        relevant_activities = relevant_activities. \
            outerjoin(order_query, order_query.c.id == Activity.id)

        # Filter by timestamp
        # @TODO: do it!
        # timestamp_filter = None

        # Decide which version a user can see.
        # - Public (not logged in) always see active versions.
        # - Logged in users see their own pending versions, as long as they are
        #   newer than the active version.
        # - Moderators see their own and other pending versions if they are
        #   within their profile, as long as they are newer than the active
        #   version.

        if logged_in and public_query is False:
            # Logged in

            # Find the latest version for each Activity, which is either ...
            latest_visible_version = self.Session.query(
                Activity.activity_identifier.label('identifier'),
                func.max(Activity.version).label('max_version')
            ). \
                join(Changeset)

            # ... active
            # ... or is pending and has changes by the current user
            visible_version_filters = [
                Activity.fk_status == 2,
                and_(
                    Activity.fk_status == 1,
                    Changeset.fk_user == request.user.id
                )
            ]

            # ... or (for moderators only) ...
            if is_moderator:
                # ... is pending and lies within the profile
                visible_version_filters.append(
                    and_(
                        Activity.fk_status == 1,
                        self._get_spatial_moderator_filter(request)
                    )
                )

            latest_visible_version = latest_visible_version. \
                filter(or_(* visible_version_filters)). \
                group_by(Activity.identifier). \
                subquery()

            relevant_activities = relevant_activities. \
                join(latest_visible_version, and_(
                latest_visible_version.c.identifier == Activity.identifier,
                latest_visible_version.c.max_version == Activity.version
            ))

        else:
            # Public (not logged in): show only active
            # TODO: make this more dynamic?
            relevant_activities = relevant_activities. \
                filter(Activity.fk_status == 2)

        relevant_activities = relevant_activities. \
            group_by(Activity.id, order_query.c.value, Activity.fk_status,
                     Activity.activity_identifier)

        # Filter based on Stakeholder attributes
        if sh_filter_length > 0:
            # Prepare a dict to simulate filter for Stakeholders
            sh_filter_dict = {
                'sh_tag_filter': sh_tag_filter,
                'sh_filter_length': sh_filter_length,
                'status_filter': status_filter
            }
            # Use StakeholderProtocol to query id's of Stakeholders
            from lokp.protocols.stakeholder_protocol import StakeholderProtocol
            sp = StakeholderProtocol(self.Session)
            rel_sh = sp._get_relevant_stakeholders_many(
                request, filter=sh_filter_dict)
            sh_query = sp._query_only_id(rel_sh)
            sh_subquery = sh_query.subquery()
            if self._get_logical_operator(request) == 'or':
                # OR: use 'union' to add id's to relevant_activities
                relevant_activities = relevant_activities. \
                    union(self.Session.query(
                    Activity.id.label('order_id'),
                    func.char_length('').label('order_value'),  # dummy
                    Activity.fk_status,
                    Activity.activity_identifier
                ).
                          join(Involvement).
                          join(sh_subquery, sh_subquery.c.id ==
                               Involvement.fk_stakeholder).
                          group_by(Activity.id))
            else:
                # AND: filter id's of relevant_activities
                relevant_activities = relevant_activities. \
                    join(Involvement). \
                    join(sh_subquery, sh_subquery.c.id ==
                         Involvement.fk_stakeholder). \
                    group_by(Activity.id)

        # Do the ordering
        if order_numbers is not None:
            if self._get_order_direction(request) == 'DESC':
                # Descending
                if order_numbers is True:
                    # Order by numbers: Cast values to float
                    relevant_activities = relevant_activities.order_by(
                        desc(cast(order_query.c.value, Float)))
                else:
                    # Order alphabetically
                    relevant_activities = relevant_activities.order_by(
                        desc(order_query.c.value))
            else:
                # Ascending
                if order_numbers is True:
                    # Order by numbers: Cast values to float
                    relevant_activities = relevant_activities.order_by(
                        asc(cast(order_query.c.value, Float)))
                else:
                    # Order alphabetically
                    relevant_activities = relevant_activities.order_by(
                        asc(order_query.c.value))

        return relevant_activities

    def _get_relevant_activities_by_stakeholders(
            self, request, uids, public_query=False):

        logged_in, is_moderator = self._get_user_status(
            effective_principals(request))

        # Use StakeholderProtocol to query the Stakeholder versions
        # corresponding to given uid
        from lokp.protocols.stakeholder_protocol import StakeholderProtocol
        sp = StakeholderProtocol(self.Session)

        if len(uids) == 1:
            # Query only 1 Stakeholder
            relevant_stakeholders = sp._get_relevant_stakeholders_one(
                request, uid=uids[0], public_query=public_query)
        elif isinstance(uids, list):
            raise HTTPBadRequest(detail='Not yet supported')
        else:
            raise HTTPNotFound()

        relevant_stakeholders = relevant_stakeholders. \
            subquery()

        # Prepare status filter
        status_filter = self.Session.query(
            Status.id
        ). \
            filter(or_(* self._get_status(request)))

        # Prepare order: Get the order from request
        order_query, order_numbers = self._get_order(
            request, Activity, A_Tag_Group, A_Tag, A_Key, A_Value)

        # Create relevant Activities
        relevant_activities = self.Session.query(
            Activity.id.label('order_id'),
            order_query.c.value.label('order_value'),
            Activity.fk_status,
            Activity.activity_identifier
        )

        # Filter trough Involvements to only take Activities involved with
        # relevant Stakeholder
        relevant_activities = relevant_activities. \
            join(Involvement). \
            filter(Involvement.fk_stakeholder.in_(
            select([relevant_stakeholders.c.order_id])
        ))

        # Join Activities with Tag Groups and order_query, then group it
        relevant_activities = relevant_activities. \
            outerjoin(A_Tag_Group). \
            outerjoin(order_query, order_query.c.id == Activity.id). \
            filter(Activity.fk_status.in_(status_filter))

        # If logged in and it is not a public query, add pending versions by
        # current user to selection. If moderator, add all pending versions.
        if logged_in and public_query is False:

            # It is necessary to first find out, if there are Activities
            # pending and if yes, which is the latest version
            latest_pending_activities = self.Session.query(
                Activity.activity_identifier,
                func.max(Activity.version).label('max_version')
            ). \
                join(Changeset). \
                filter(or_(Activity.fk_status == 1, Activity.fk_status == 2))

            if not is_moderator:
                # If current user is not a moderator, only show pending
                # versions done by himself
                latest_pending_activities = latest_pending_activities. \
                    filter(Changeset.fk_user == request.user.id)

            latest_pending_activities = latest_pending_activities. \
                group_by(Activity.activity_identifier). \
                subquery()

            # Collect other information about pending Activities (order, ...)
            pending_activities = self.Session.query(
                Activity.id.label('order_id'),
                order_query.c.value.label('order_value'),
                Activity.fk_status,
                Activity.activity_identifier
            ). \
                join(latest_pending_activities, and_(
                latest_pending_activities.c.max_version
                == Activity.version,
                latest_pending_activities.c.activity_identifier
                == Activity.activity_identifier
            ))

            # Filter trough Involvements to only take Activities involved with
            # relevant Stakeholder
            pending_activities = pending_activities. \
                join(Involvement). \
                filter(Involvement.fk_stakeholder.in_(
                select([relevant_stakeholders.c.order_id])
            ))

            # Join Activities with Tag Groups and order_query, then group it
            pending_activities = pending_activities. \
                outerjoin(A_Tag_Group). \
                outerjoin(order_query, order_query.c.id == Activity.id). \
                group_by(Activity.activity_identifier, Activity.id,
                         order_query.c.value)

            # Filter out the active Activities if they have a pending version.
            # Then union with pending Activities.
            relevant_activities = relevant_activities.filter(
                not_(Activity.activity_identifier.in_(
                    select(
                        [pending_activities.subquery().c.activity_identifier])
                ))
            )
            relevant_activities = pending_activities.union(
                relevant_activities)

        relevant_activities = relevant_activities. \
            group_by(Activity.id, order_query.c.value, Activity.fk_status,
                     Activity.activity_identifier)

        # Do the ordering
        if order_numbers is not None:
            if self._get_order_direction(request) == 'DESC':
                # Descending
                if order_numbers is True:
                    # Order by numbers: Cast values to float
                    relevant_activities = relevant_activities.order_by(
                        desc(cast(order_query.c.value, Float)))
                else:
                    # Order alphabetically
                    relevant_activities = relevant_activities.order_by(
                        desc(order_query.c.value))
            else:
                # Ascending
                if order_numbers is True:
                    # Order by numbers: Cast values to float
                    relevant_activities = relevant_activities.order_by(
                        asc(cast(order_query.c.value, Float)))
                else:
                    # Order alphabetically
                    relevant_activities = relevant_activities.order_by(
                        asc(order_query.c.value))

        return relevant_activities

    def _query_only_id(self, relevant_activities):
        # Create query
        relevant_activities = relevant_activities.subquery()
        query = self.Session.query(
            Stakeholder.id.label('id')
        ). \
            join(relevant_activities,
                 relevant_activities.c.order_id == Stakeholder.id)

        return query

    def _query_history(
            self, relevant_activities, limit=None, offset=None,
            return_count=True):

        # Count
        if return_count:
            count = relevant_activities.count()

        # Apply limit and offset
        if limit is not None:
            relevant_activities = relevant_activities.limit(limit)
        if offset is not None:
            relevant_activities = relevant_activities.offset(offset)

        # Create query
        relevant_activities = relevant_activities.subquery()
        query = self.Session.query(
            Activity.activity_identifier.label('identifier'),
            Activity.version.label('version'),
            Status.id.label('status_id'),
            Status.name.label('status'),
            Changeset.timestamp.label('timestamp'),
            User.username.label('user_name')
        ). \
            join(relevant_activities,
                 relevant_activities.c.order_id == Activity.id). \
            join(Status). \
            join(Changeset). \
            join(User, User.id == Changeset.fk_user)

        if return_count:
            return query, count
        else:
            return query

    def _query_many(
            self, request, relevant_activities, limit=None, offset=None,
            involvements=False, return_count=True, metadata=False):
        # Prepare query to translate keys and values
        localizer = get_localizer(request)
        lang = self.Session.query(
            Language
        ). \
            filter(Language.locale == localizer.locale_name). \
            first()
        key_translation, value_translation = self._get_translatedKV(
            lang, A_Key, A_Value
        )

        # All object instances need to be removed from the current session in
        # order to continue. Otherwise results in DetachedInstanceError error
        # (http://sqlalche.me/e/bhk3)
        self.Session.expunge_all()

        # Count
        if return_count:
            count = relevant_activities.count()

        # Apply limit and offset
        if limit is not None:
            relevant_activities = relevant_activities.limit(limit)
        if offset is not None:
            relevant_activities = relevant_activities.offset(offset)

        # Create query
        relevant_activities = relevant_activities.subquery()
        query = self.Session.query(
            Activity.id.label('id'),
            Activity.activity_identifier.label('identifier'),
            Activity.point.label('geometry'),
            Activity.version.label('version'),
            Status.id.label('status_id'),
            Status.name.label('status'),
            Changeset.timestamp.label('timestamp'),
            A_Tag_Group.id.label('taggroup'),
            A_Tag_Group.tg_id.label('tg_id'),
            A_Tag_Group.fk_a_tag.label('main_tag'),
            A_Tag.id.label('tag'),
            A_Key.key.label('key'),
            A_Value.value.label('value'),
            key_translation.c.key_translated.label('key_translated'),
            value_translation.c.value_translated.label('value_translated'),
            relevant_activities.c.order_value.label('order_value')
        ). \
            join(relevant_activities,
                 relevant_activities.c.order_id == Activity.id). \
            join(Status). \
            join(Changeset). \
            outerjoin(A_Tag_Group). \
            outerjoin(A_Tag, A_Tag_Group.id == A_Tag.fk_a_tag_group). \
            outerjoin(A_Key). \
            outerjoin(A_Value, A_Tag.fk_value == A_Value.id). \
            outerjoin(key_translation,
                      key_translation.c.key_original_id == A_Key.id). \
            outerjoin(value_translation,
                      value_translation.c.value_original_id == A_Value.id)

        # Do the ordering again: A first ordering was done when creating the
        # relevant activities. However, it is necessary to restore this
        # ordering after all the additional data was added through this query.
        order_query, order_numbers = self._get_order(
            request, Activity, A_Tag_Group, A_Tag, A_Key, A_Value
        )
        if order_query is not None:
            if self._get_order_direction(request) == 'DESC':
                query = query.order_by(desc(relevant_activities.c.order_value))
            else:
                query = query.order_by(asc(relevant_activities.c.order_value))

        if metadata:
            query = query.add_columns(
                Activity.previous_version.label('previous_version'),
                User.id.label('user_id'),
                User.username.label('user_name'),
                User.firstname.label('user_firstname'),
                User.lastname.label('user_lastname'),
                User.privacy.label('user_privacy'),
                Institution.id.label('institution_id'),
                Institution.name.label('institution_name'),
                Institution.url.label('institution_url'),
                Institution.logo_url.label('institution_logo'),
            ). \
                outerjoin(User, User.id == Changeset.fk_user). \
                outerjoin(Institution)

        if involvements:
            inv_status_filter = self.Session.query(
                Status.id
            ). \
                filter(or_(* self._get_involvement_status(request)))

            # Additional filter to select only the latest (pending or not)
            # Stakeholder involved with the relevant Activities
            latest_filter = self.Session.query(
                Stakeholder.stakeholder_identifier,
                Involvement.fk_activity,
                func.max(Stakeholder.version).label('max_version')
            ). \
                join(Involvement). \
                join(relevant_activities, relevant_activities.c.order_id ==
                     Involvement.fk_activity). \
                group_by(Stakeholder.stakeholder_identifier,
                         Involvement.fk_activity). \
                subquery()

            inv_status = self.Session.query(
                Stakeholder.id.label('stakeholder_id'),
                Stakeholder.stakeholder_identifier.
                    label('stakeholder_identifier'),
                Stakeholder.fk_status.label('stakeholder_status'),
                Stakeholder.version.label('stakeholder_version'),
                Stakeholder.fk_changeset.label('changeset_id')
            ). \
                filter(Stakeholder.fk_status.in_(inv_status_filter)). \
                join(Involvement). \
                join(latest_filter, and_(
                latest_filter.c.max_version == Stakeholder.version,
                latest_filter.c.stakeholder_identifier
                == Stakeholder.stakeholder_identifier,
                latest_filter.c.fk_activity == Involvement.fk_activity
            )). \
                subquery()
            inv_query = self.Session.query(
                Involvement.fk_activity.label('activity_id'),
                Stakeholder_Role.id.label('role_id'),
                Stakeholder_Role.name.label('role_name'),
                Changeset.fk_user.label('stakeholder_user_id'),
                inv_status.c.stakeholder_identifier.
                    label('stakeholder_identifier'),
                inv_status.c.stakeholder_status.label('stakeholder_status'),
                inv_status.c.stakeholder_version.
                    label('stakeholder_version')
            ). \
                join(inv_status, inv_status.c.stakeholder_id ==
                     Involvement.fk_stakeholder). \
                join(Changeset, Changeset.id == inv_status.c.changeset_id). \
                join(Stakeholder_Role). \
                subquery()

            #log.debug("Involvement Query:\n%s" % inv_query)

            query = query. \
                add_columns(
                inv_query.c.stakeholder_identifier.label(
                    'stakeholder_identifier'),
                inv_query.c.role_name.label('stakeholder_role'),
                inv_query.c.role_id.label('stakeholder_role_id'),
                inv_query.c.stakeholder_status.label('stakeholder_status'),
                inv_query.c.stakeholder_version.label(
                    'stakeholder_version'),
                inv_query.c.stakeholder_user_id.label(
                    'stakeholder_user_id')
            ). \
                outerjoin(inv_query, inv_query.c.activity_id == Activity.id)

        if return_count:
            return query, count
        else:
            return query

    def _query_taggroup_geojson(
            self, request, relevant_activities, translate=True):
        """
        Query all taggroups of an Activity version which have a geometry
        """

        categoryList = getCategoryList(request, 'activities')
        attrs = categoryList.getMainkeyWithGeometry()
        origAttrs = [a[1] for a in attrs]

        relevant_activities = relevant_activities.subquery()

        query = self.Session.query(
            Activity.id.label('id'),
            A_Tag_Group.id.label('tgid'),
            A_Tag_Group.geometry.label('geometry')
        ). \
            join(relevant_activities,
                 relevant_activities.c.order_id == Activity.id). \
            outerjoin(A_Tag_Group, Activity.id == A_Tag_Group.fk_activity). \
            outerjoin(A_Tag, A_Tag_Group.id == A_Tag.fk_a_tag_group). \
            outerjoin(A_Key, A_Tag.fk_key == A_Key.id). \
            outerjoin(A_Value, A_Tag.fk_value == A_Value.id). \
            filter(A_Tag_Group.geometry != None)

        if len(origAttrs) > 0:
            query = query.filter(A_Key.key.in_(origAttrs))

        if translate is True:
            localizer = get_localizer(request)
            dbLang = self.Session.query(Language). \
                filter(Language.locale == localizer.locale_name). \
                first()

        if translate is True and dbLang is not None:
            key_translation, value_translation = self._get_translatedKV(
                dbLang, A_Key, A_Value)
            query = query.add_columns(
                A_Key.key.label('key'),
                key_translation.c.key_translated.label('key_translated'),
                A_Value.value.label('value'),
                value_translation.c.value_translated.label('value_translated')
            )
            query = query. \
                outerjoin(
                key_translation,
                key_translation.c.key_original_id == A_Key.id). \
                outerjoin(
                value_translation,
                value_translation.c.value_original_id == A_Value.id)

        else:
            query = query.add_columns(
                A_Key.key.label('key'),
                A_Value.value.label('value')
            )

        return query

    def _query_geojson(
            self, request, relevant_activities, limit=None, offset=None,
            attrs=[], tggeom=None, dbLang=None, translate=False,
            translateKeys=False):

        # Apply limit and offset
        if limit is not None:
            relevant_activities = relevant_activities.limit(limit)
        if offset is not None:
            relevant_activities = relevant_activities.offset(offset)

        # Create query
        relevant_activities = relevant_activities.subquery()
        # Caution: If you change something here (add or remove columns), adapt
        # the number in function _query_to_geojson as well!
        query = self.Session.query(
            Activity.id.label('id'),
            Activity.point.label('geometry'),
            Activity.activity_identifier.label('identifier'),
            Activity.version.label('version'),
            Status.id.label('status_id'),
            Status.name.label('status_name')
        ). \
            join(relevant_activities,
                 relevant_activities.c.order_id == Activity.id). \
            join(Status)

        if len(attrs) > 0:
            origAttrs = [a[0] for a in attrs]
            query = query. \
                outerjoin(
                A_Tag_Group, Activity.id == A_Tag_Group.fk_activity). \
                outerjoin(A_Tag, A_Tag_Group.id == A_Tag.fk_a_tag_group). \
                outerjoin(A_Key, A_Tag.fk_key == A_Key.id). \
                outerjoin(A_Value, A_Tag.fk_value == A_Value.id)

            if len(origAttrs) > 0:
                query = query.filter(A_Key.key.in_(origAttrs))

            if translate is not False and dbLang is not None:
                key_translation, value_translation = self._get_translatedKV(
                    dbLang, A_Key, A_Value)
                query = query.add_columns(
                    A_Value.value,
                    value_translation.c.value_translated
                )
                query = query. \
                    outerjoin(
                    value_translation,
                    value_translation.c.value_original_id == A_Value.id)
            else:
                query = query.add_columns(A_Value.value, A_Value.value)

            if tggeom is not None:
                query = query.add_columns(A_Tag_Group.geometry)
                query = query.filter(A_Tag_Group.geometry != None)

        return query

    def _query_to_history(self, query):

        # Put the Activities together
        activities = []
        for q in query.all():
            activities.append({
                'identifier': str(q.identifier),
                'version': q.version,
                'statusId': q.status_id,
                'statusName': q.status,
                'timestamp': datetime.datetime.strftime(
                    q.timestamp, '%Y-%m-%d %H:%M:%S'),
                'username': q.user_name
            })
        return activities

    def _query_to_activities(self, request, query, involvements='none',
                             public_query=False, **kwargs):

        geom = kwargs.get('geom', False)
        if geom is True:
            query = query.add_columns(
                A_Tag_Group.geometry.label('tg_geometry')
            )
        translate = kwargs.get('translate', True)

        logged_in, is_moderator = self._get_user_status(
            effective_principals(request))

        # Put the Activities together
        activities = []
        for q in query.all():

            # Prepare values if needed
            identifier = str(q.identifier)
            taggroup_id = int(q.taggroup) if q.taggroup is not None else None
            key = (q.key_translated if q.key_translated is not None
                                       and translate is not False else q.key)
            value = (q.value_translated if q.value_translated is not None
                                           and translate is not False else q.value)

            # Use UID and version to find existing ActivityFeature or create a
            # new one
            activity = None
            for a in activities:
                if a.get_guid() == identifier and a.get_version() == q.version:
                    if not isinstance(q.order_value, int):
                        if a.get_order_value() == q.order_value:
                            activity = a
                    else:
                        activity = a

            if activity is None:
                # Handle optional metadata correctly
                previous_version = q.previous_version if hasattr(
                    q, 'previous_version') else None
                user_privacy = q.user_privacy if hasattr(
                    q, 'user_privacy') else None
                user_id = q.user_id if hasattr(q, 'user_id') else None
                user_name = q.user_name if hasattr(q, 'user_name') else None
                user_firstname = q.user_firstname if hasattr(
                    q, 'user_firstname') else None
                user_lastname = q.user_lastname if hasattr(
                    q, 'user_lastname') else None
                institution_id = q.institution_id if hasattr(
                    q, 'institution_id') else None
                institution_name = q.institution_name if hasattr(
                    q, 'institution_name') else None
                institution_url = q.institution_url if hasattr(
                    q, 'institution_url') else None
                institution_logo = q.institution_logo if hasattr(
                    q, 'institution_logo') else None

                activity = ActivityFeature(
                    identifier, q.order_value, geometry=q.geometry,
                    version=q.version, status=q.status, status_id=q.status_id,
                    timestamp=q.timestamp, user_privacy=user_privacy,
                    institution_id=institution_id,
                    institution_name=institution_name,
                    institution_url=institution_url,
                    institution_logo=institution_logo, user_id=user_id,
                    user_name=user_name, user_firstname=user_firstname,
                    user_lastname=user_lastname,
                    previous_version=previous_version)
                activities.append(activity)

            # Check if current Tag Group is already present in the Activity
            taggroup = None
            if activity.find_taggroup_by_id(taggroup_id) is not None:
                taggroup = activity.find_taggroup_by_id(taggroup_id)
            elif key:
                taggroup = TagGroup(taggroup_id, q.tg_id, q.main_tag)
                # Set the taggroup geometry if available
                if geom is True and q.tg_geometry is not None:
                    taggroup.set_geometry(q.tg_geometry)
                activity.add_taggroup(taggroup)

            # Because of Involvements, the same Tags appears for each
            # Involvement, so add it only once to TagGroup
            if taggroup is not None and taggroup.get_tag_by_id(q.tag) is None:
                taggroup.add_tag(Tag(q.tag, key, value))

            # Involvements
            if involvements != 'none':

                try:
                    if q.stakeholder_identifier is not None:

                        try:
                            request_user_id = request.user.id
                        except AttributeError:
                            request_user_id = None

                        # Only proceed if
                        # If there are multiple pending versions of the same
                        # Stakeholder, show only the latest one (highest
                        # version)
                        newer_pending_exists = False
                        if q.stakeholder_status == 1:
                            for p_i in activity._involvements:
                                if (p_i.get_guid() == q.stakeholder_identifier
                                        and p_i.get_status() in [1, 2]):
                                    if (p_i.get_version() >
                                            q.stakeholder_version):
                                        newer_pending_exists = True
                                    else:
                                        activity.remove_involvement(p_i)

                        # Flag indicating if Involvement to this Activity is
                        # not yet found ('none') or not to be added ('false')
                        inv = self._flag_add_involvement(
                            activity, q.status_id, q.stakeholder_status,
                            q.stakeholder_identifier, q.stakeholder_version,
                            q.stakeholder_user_id, q.stakeholder_role,
                            request_user_id, public_query, logged_in,
                            is_moderator)

                        if inv is None and newer_pending_exists is False:
                            # Create new Involvement and add it to Activity
                            # Default: only basic information about Involvement
                            activity.add_involvement(Inv(
                                q.stakeholder_identifier, None,
                                q.stakeholder_role, q.stakeholder_role_id,
                                q.stakeholder_version, q.stakeholder_status))
                except ValueError:
                    pass

        if involvements == 'full':
            # If full involvements are to be shown, collect the identifiers and
            # versions of each Stakeholder and prepare a dict. Query the
            # details (Tag Groups) of these Stakeholders using the
            # ActivityProtocol and replace the existing Involvements. Query
            # them all at once to improve performance.

            inv_dicts = []
            for activity in activities:
                for i in activity._involvements:
                    inv_dicts.append({
                        'identifier': i.get_guid(),
                        'version': i.get_version()
                    })

            # Use StakeholderProtocol to query the details of the Activities
            from lokp.protocols.stakeholder_protocol import StakeholderProtocol
            sp = StakeholderProtocol(self.Session)
            relevant_stakeholders = sp._get_relevant_stakeholders_dict(
                request, inv_dicts)

            sh_query = sp._query_many(
                request, relevant_stakeholders, involvements=False,
                return_count=False)
            stakeholders = sp._query_to_stakeholders(
                request, sh_query, involvements='none')

            # Loop through all existing Involvements
            for activity in activities:
                for index, i in enumerate(activity._involvements):
                    # Try to find the current Activity in the detailed list
                    stakeholder = None
                    for sh in stakeholders:
                        if (str(sh.get_guid()) == str(i.get_guid())
                                and sh.get_version() == i.get_version()):
                            stakeholder = sh

                    if stakeholder is not None:
                        # If Activity was found, replace Involvement with full
                        # details
                        activity._involvements[index] = Inv(
                            i.get_guid(), stakeholder, i.get_role(),
                            i.get_role_id(), i.get_version(), i.get_status())

        return activities

    def _query_to_taggroup_geojson(self, query, translate=True):

        def _create_feature(id, g, d):
            """
            Small helper function to create a new Feature with an id, a
            geometry and a dict as properties
            """
            feature = {}

            feature['geometry'] = geometry_as_geojson(g)
            feature['properties'] = d
            feature['fid'] = int(id)
            feature['id'] = int(id)
            feature['type'] = 'Feature'

            return feature

        features = []

        for q in query.all():

            k = q.key
            if translate is True and q.key_translated is not None:
                k = q.key_translated
            v = q.value
            if translate is True and q.value_translated is not None:
                v = q.value_translated

            # Activity ID is useless, use the taggroup ID as id
            features.append(_create_feature(q.tgid, q.geometry, {k: v}))

        featureCollection = {}
        featureCollection['features'] = features
        featureCollection['type'] = 'FeatureCollection'

        return featureCollection

    def _query_to_geojson(self, query, attrs=[], tggeom=None):

        def _create_feature(
                id, g, identifier, status_id, status_name, version, keys,
                values):
            """
            Small helper function to create a new Feature
            """
            feature = {
                'geometry': geometry_as_geojson(g),
            }

            properties = {
                'status': status_name,
                'status_id': status_id,
                'activity_identifier': str(identifier),
                'version': int(version)
            }
            for i, k in enumerate(keys):
                key = k[1]
                value = (
                    values[i + 1] if values[i + 1] is not None else values[i])
                properties[key] = value
            feature['properties'] = properties

            # Doppelt genaeht haelt besser
            feature['fid'] = int(id)
            feature['id'] = int(id)
            feature['type'] = 'Feature'

            return feature

        featureCollection = {}
        featureCollection['features'] = []
        featureCollection['type'] = 'FeatureCollection'

        for q in query.all():
            additionalValues = []
            # Caution: This number is strongly correlated with the number of
            # columns set when creating the query in function _query_geojson
            # above.
            if len(q) > 6 and len(attrs) > 0:
                additionalValues = q[6:]

            if ((tggeom is not None and len(attrs) * 2 + 1
                 != len(additionalValues))
                    or (tggeom is None and len(attrs) * 2 !=
                        len(additionalValues))):
                # If the additionalKeys and additionalValues do not match,
                # ignore them completely.
                # Keep in mind that for tg!=None, the taggroup geometry is also
                # one of the additionalValues.
                attrs = []
                additionalValues = []

            featureCollection['features'].append(_create_feature(
                q.id, q.geometry, q.identifier, q.status_id, q.status_name,
                q.version, attrs, additionalValues))

        return featureCollection

    def _get_spatial_moderator_filter(self, request):
        """
        Create an array of geometry filters based on the user's profile(s)
        """
        userid = request.user.username  # authenticated_userid(request)

        profile_filters = []

        if userid is not None:
            profiles = self.Session.query(Profile). \
                filter(Profile.users.any(username=userid))
            for p in profiles.all():
                profile_filters.append(Activity.point.intersects(p.geometry))
                if p.code == 'global':
                    profile_filters.append(Activity.point == None)

        if len(profile_filters) > 0:
            return or_(* profile_filters)

        return None

    def _get_bbox_filter(self, request, cookies=True):
        """
        Return a spatial filter for the point of Activities based on the
        bounding box parameters found in the request.

        If a valid bounding box was found, a GeoAlchemy function
        intersecting the point geometries of Activities with the
        bounding box geometry is returned. This function can then be
        used as a filter in SQLAlchemy.

        Args:
            request (pyramid.request): A Pyramid Request object.

        Kwargs:
            cookies (bool): A boolean indicating whether to look for a
                location cookie as fallback if no request parameters
                were provided. This argument is passed to the
                `get_bbox_parameters` function.

        Returns:
            geoalchemy.functions.intersects or None. A GeoAlchemy
            function which intersects the points of Activities with the
            bounding box geometry. None if no valid bounding box was
            found.
        """

        bbox, epsg = get_bbox_parameters(request, cookies=cookies)
        box = validate_bbox(bbox)

        if box is None:
            return None

        geometry = Polygon((
            (box[0], box[1]),
            (box[0], box[3]),
            (box[2], box[3]),
            (box[2], box[1]),
            (box[0], box[1])))

        # Create the intersection geometry
        wkb_geometry = from_shape(geometry, epsg)

        # Get the SRID used in the Activity class
        activity_srid = geofunctions.ST_SRID(Activity.point)

        # Return a subquery
        return geofunctions.ST_Intersects(
            Activity.point,
            geofunctions.ST_Transform(wkb_geometry, activity_srid))

    def _get_profile_filter(self, request):
        """
        Return a spatial filter based on the profile boundary of the current
        profile which is queried from the database.
        """

        profile = self.Session.query(Profile). \
            filter(Profile.code == get_current_profile(request)). \
            first()

        if profile is None:
            return (Activity.id == 0)

        return Activity.point.intersects(profile.geometry)

    def _handle_activity(self, request, activity_dict, changeset,
                         status='pending'):
        """
        Handles a single Activity and decides whether to create a new Activity
        or update an existing one.
        """

        # Collect information about changing involvements
        involvement_change = (activity_dict['stakeholders']
        if 'stakeholders' in activity_dict
        else None)
        implicit_inv_change = (True
        if involvement_change is not None and
           'implicit_involvement_update' in activity_dict
           and activity_dict['implicit_involvement_update']
           is True else False)

        create_new = False

        # If there is no id for the Activity in the diff, create a new Activity
        if 'id' not in activity_dict:
            create_new = True
        else:
            # If there is an ID in the diff, try to find the Activity based on
            # the identifier and version
            identifier = activity_dict['id']
            old_version = (activity_dict['version']
            if 'version' in activity_dict else None)
            db_a = self.Session.query(Activity). \
                filter(Activity.activity_identifier == identifier). \
                filter(Activity.version == old_version). \
                first()
            if db_a is None:
                # If no Activity was found, create a new one
                create_new = True

        if create_new is True:
            # Create new Activity
            new_activity = self._create_activity(
                request, activity_dict, changeset, status=status
            )

            if new_activity is not None:
                # Handle also the involvements
                self._handle_involvements(
                    request, None, new_activity, involvement_change, changeset,
                    implicit_inv_change
                )

            return new_activity, None

        else:
            # Update existing Activity
            updated_activity, return_diff = self._update_object(
                request, db_a, activity_dict, changeset
            )

            # Handle also the involvements
            self._handle_involvements(
                request, db_a, updated_activity, involvement_change, changeset,
                implicit_inv_change)

            return updated_activity, return_diff

    def _create_activity(self, request, activity_dict, changeset, ** kwargs):
        """
        Creates a new Activity and handles its involvements.
        Allowed keyword arguments:
        - 'status'
        """

        # First check if all the needed values are in the activity_dict:
        # At least one taggroup needs to be in the diff.
        if 'taggroups' not in activity_dict:
            return None

        identifier = (activity_dict['id'] if 'id' in activity_dict and
                                             activity_dict['id'] is not None
        else str(uuid.uuid4()))

        # The initial version is 1
        version = 1

        # Try to get the geometry
        if ('geometry' in activity_dict and activity_dict['geometry']
                is not None):

            geom = geojson.loads(
                json.dumps(activity_dict['geometry']),
                object_hook=geojson.GeoJSON.to_instance)

            # The geometry (shapely deals with geometries, not with features or feature collections)

            shape = asShape(geom)

            try:
                geometrytype = shape.geom_type
            except:
                raise HTTPBadRequest(detail="Invalid geometry type.")

            if geometrytype == 'Polygon':
                g = shape.wkt
            else:
                g = shape.representative_point().wkt

            geom_transformed = WKTElement(g, srid=4326)

            # Create a new activity and add representative point to the
            # activity
            new_activity = Activity(activity_identifier=identifier,
                                    version=version, point=geom_transformed)

        else:
            # Activities cannot be created if they do not have a geometry
            raise HTTPBadRequest(detail="No geometry provided!")

        # Status (default: 'pending')
        status = 'pending'
        if 'status' in kwargs:
            status = kwargs['status']
        new_activity.status = self.Session.query(Status). \
            filter(Status.name == status). \
            first()

        # Initialize Tag Groups
        new_activity.tag_groups = []

        # Append the Changeset
        new_activity.changeset = changeset

        # Add the Activity to the database
        self.Session.add(new_activity)

        # Store the current profile when creating a new Activity
        profile_code = get_current_profile(request)
        profile = self.Session.query(
            Profile
        ). \
            filter(Profile.code == profile_code). \
            first()

        new_activity.profile = profile

        # Populate the Tag Groups
        for i, taggroup in enumerate(activity_dict['taggroups']):

            # Main Tag: First reset it. Then try to get it (its key and value)
            # from the dict.
            # The Main is indeed mandatory.
            try:
                main_tag = taggroup['main_tag']
                main_tag_key = main_tag['key']
                main_tag_value = main_tag['value']
            except KeyError:
                raise HTTPBadRequest(
                    detail="No Main Tag provided. Taggroup %s has no taggroup."
                           % taggroup)

            db_tg = A_Tag_Group(i + 1)
            new_activity.tag_groups.append(db_tg)

            # get config_taggroup
            category_list = getCategoryList(request, 'activities')
            _, _, config_taggroup = category_list.findCategoryThematicgroupTaggroupByMainkey(main_tag_key)

            # Loop all tags within a tag group
            for tag in taggroup['tags']:

                # Add the tag only if the op property is set to add
                if 'op' not in tag:
                    continue
                elif tag['op'] != 'add':
                    continue

                # Get the key and the value of the current tag
                key = tag['key']
                value = tag['value']

                if key.startswith('map'):
                    if config_taggroup.getMap() is not None:
                        # Add geometry to taggroup and not create tag
                        geometry = value.get('geometry')
                        taggroup['geometry'] = geometry
                        taggroup
                        continue


                # Create the new tag
                a_tag = self._create_tag(
                    request, db_tg.tags, key, value, A_Tag, A_Key, A_Value)

                # Check if the current tag is the main tag of this tag group.
                # If yes, set the main_tag attribute to this tag
                try:
                    if (a_tag.key.key == main_tag_key
                            and str(a_tag.value.value)
                            == str(main_tag_value)):
                        db_tg.main_tag = a_tag
                except AttributeError:
                    pass

            # Check that a Main Tag was set.
            # If none was set (if it did not match any of the keys of the
            # taggroup), raise an error.
            if db_tg.main_tag is None:
                raise HTTPBadRequest(
                    detail='Invalid Main Tag provided. The Taggroup %s has no '
                           'valid Main Tag' % taggroup)

            # If available, try to handle the geometry of a taggroup
            try:

                tg_geom_diff = taggroup['geometry']
                tg_geom = geojson.loads(tg_geom_diff)
                # The geometry
                try:
                    tg_shape = asShape(tg_geom)
                    geometrytype = tg_shape.geom_type
                except:
                    raise HTTPBadRequest(
                        detail="Invalid geometry type of taggroup")
                # Store the geometry only if it is a polygon or multipolygon
                if geometrytype == 'Polygon' or geometrytype == 'MultiPolygon':
                    # define right projection
                    db_tg.geometry = WKTElement(tg_shape.wkt, srid=4326)

                else:
                    raise HTTPBadRequest(
                        detail="Invalid geometry type of taggroup: Only "
                               "Polygon or MultiPolygon is supported.")
            except KeyError:
                pass

        return new_activity

    def _update_object(
            self, request, old_activity, activity_dict, changeset, ** kwargs):
        """
        Update an Activity. The basic idea is to deep copy the previous version
        and decide for each tag if it is to be deleted or not. At the end, new
        tags and new taggroups are added.
        Allowed keyword arguments:
        - 'status'
        """

        return_diff = None

        if old_activity.fk_status == 1:
            # If changes were made to a pending version, this pending version
            # is set to 'edited' and the newly created version contains also
            # the changes of the edited version. To do this, a new diff is
            # calculated which is then applied to the previous version of the
            # edited pending version.

            # Set the edited pending version to 'edited'
            old_activity.fk_status = 6

            # Query the diff of the edited pending version and recalculate it
            # with the recent changes to the pending version
            diff = json.loads(old_activity.changeset.diff)
            activity_dict = self.recalculate_diffs(
                request,
                Activity,
                old_activity.identifier,
                old_activity.version,
                activity_dict,
                diff
            )
            # Also store and return the newly calculated diff
            return_diff = activity_dict

            # Query the previous version of the edited pending version
            ref_version = self.Session.query(
                Activity
            ). \
                filter(Activity.identifier == old_activity.identifier). \
                filter(Activity.version == old_activity.previous_version). \
                first()

            if ref_version is None:
                # If there is no previous version, the edited pending version
                # is brand new.
                previous_version = None
            else:
                # Use the previous version of the edited pending version as
                # base to apply the diff on
                old_activity = ref_version
                previous_version = old_activity.version

        else:
            previous_version = old_activity.version

        # Query latest version of current Activity (used to increase version)
        latest_version = self.Session.query(Activity). \
            filter(Activity.activity_identifier == old_activity.identifier). \
            order_by(desc(Activity.version)). \
            first()

        # Geometry
        new_geom = old_activity.point
        if activity_dict is not None and 'geometry' in activity_dict:
            geojson_obj = geojson.loads(
                json.dumps(activity_dict['geometry']),
                object_hook=geojson.GeoJSON.to_instance)
            new_geom = asShape(geojson_obj)

            try:
                geometrytype = new_geom.geom_type
            except:
                raise HTTPBadRequest(detail="Invalid geometry type.")

            if geometrytype == 'MultiPoint':
                new_geom = new_geom.wkt
            else:
                new_geom = new_geom.representative_point().wkt

            new_geom = WKTElement(new_geom, srid=4326)

        # Create new Activity
        new_activity = Activity(activity_identifier=old_activity.identifier,
                                version=(latest_version.version + 1),
                                previous_version=previous_version,
                                point=new_geom)

        # Status (default: 'pending')
        status = 'pending'
        if 'status' in kwargs:
            status = kwargs['status']
        new_activity.status = self.Session.query(Status). \
            filter(Status.name == status). \
            first()

        # Initialize Tag Groups
        new_activity.tag_groups = []

        # Append the Changeset
        new_activity.changeset = changeset

        # Add it to the database
        self.Session.add(new_activity)

        log.debug(
            'Applying diff:\n%s\nto version %s of activity %s'
            % (activity_dict, previous_version, old_activity.identifier))

        a = self._apply_diff(
            request,
            Activity,
            old_activity.identifier,
            previous_version,
            activity_dict,
            new_activity,
            old_activity.version,
            db=True
        )
        return a, return_diff

    def _handle_involvements(self, request, old_version, new_version,
                             inv_change, changeset, implicit=False, **kwargs):
        """
        Handle the involvements of an Activity.
        - Activity update: copy old involvements
        - Involvement added: copy old involvements, push Stakeholder to new
            version, add new involvement
        - Involvement deleted: copy old involvements (except the one to be
            removed), push Stakeholder to new version
        - Involvement modified (eg. its role): combination of deleting and
            adding involvements
        """

        # db_object: Possibility to provide an existing database object to
        # attach the updated involvements to. This is used when reviewing
        # involvements.
        db_object = kwargs.pop('db_object', None)

        # db: Boolean to specify if the involvements are to be inserted into
        # the database or just be attached to an Activity feature
        db = kwargs.pop('db', True)

        # Use the StakeholderProtocol to handle things
        from lokp.protocols.stakeholder_protocol import StakeholderProtocol
        sp = StakeholderProtocol(self.Session)

        # It is important to keep track of all the Stakeholders where
        # involvements were deleted because they need to be pushed to a new
        # version as well
        swdi_id = []  # = Stakeholders with deleted involvements
        swdi_version = []
        swdi_role = []
        # Copy old involvements if existing
        if old_version is not None:
            old_involvements = (
                old_version.involvements if db is True
                else old_version.get_involvements())
            for oi in old_involvements:
                # Check if involvement is to be removed (op == delete), in
                # which case do not copy it
                remove = False
                if inv_change is not None:
                    for i in inv_change:
                        oi_stakeholder_identifier = (
                            str(oi.stakeholder.stakeholder_identifier)
                            if db is True else oi._feature.get_guid())
                        oi_role_id = (
                            oi.stakeholder_role.id if db is True
                            else oi.get_role_id())
                        if ('id' in i and str(i['id']) ==
                                oi_stakeholder_identifier and
                                'op' in i and i['op'] == 'delete'
                                and 'role' in i and i['role'] == oi_role_id):
                            # Set flag to NOT copy this involvement
                            remove = True
                            # Add identifier and version of Stakeholder to list
                            # with deleted involvements, add them only once
                            if i['id'] not in swdi_id:
                                swdi_id.append(i['id'])
                                swdi_version.append(i['version'])
                                swdi_role.append(i['role'])
                # Also: only copy involvements if status of Stakeholder is
                # 'pending' or 'active'
                oi_status_id = (
                    oi.stakeholder.status.id if db is True
                    else oi._feature.get_status_id())
                if remove is not True and oi_status_id < 3:
                    # Copy involvement
                    if db is True:
                        sh_role = oi.stakeholder_role
                        sh = oi.stakeholder
                        inv = Involvement()
                        inv.stakeholder = sh
                        inv.activity = new_version
                        inv.stakeholder_role = sh_role
                        self.Session.add(inv)
                    else:
                        # For comparison, it is not necessary to copy the
                        # Stakeholder because it is already there.
                        pass

        # Add new involvements
        if inv_change is not None:
            for i in inv_change:
                if ('op' in i and i['op'] == 'add' and
                        'id' in i and 'role' in i and 'version' in i):
                    # Query database to find role and previous version of
                    # Stakeholder
                    role_db = self.Session.query(Stakeholder_Role). \
                        get(i['role'])
                    old_sh_db = self.Session.query(Stakeholder). \
                        filter(Stakeholder.stakeholder_identifier == i['id']). \
                        filter(Stakeholder.version == i['version']). \
                        first()
                    if old_sh_db is not None:
                        # If the same Stakeholder also has some involvements
                        # deleted, remove it from the list (do not push
                        # Stakeholder twice)

                        if db is True:
                            # Push Stakeholder to new version
                            # Simulate a dict
                            sh_dict = {
                                'id': old_sh_db.stakeholder_identifier,
                                'version': old_sh_db.version
                            }

                            if db_object is not None:
                                new_sh = db_object
                            else:
                                new_sh, new_diff = sp._handle_stakeholder(
                                    request, sh_dict, changeset
                                )

                            try:
                                x = swdi_id.index(
                                    str(old_sh_db.stakeholder_identifier))

                                for inv in new_sh.involvements:
                                    if inv.activity == old_version:
                                        self.Session.delete(inv)

                                swdi_id.pop(x)
                                swdi_version.pop(x)
                                swdi_role.pop(x)

                            except ValueError:
                                pass

                            # Create new inolvement
                            inv = Involvement()
                            inv.stakeholder = new_sh
                            inv.activity = new_version
                            inv.stakeholder_role = role_db
                            self.Session.add(inv)
                        else:
                            # The 'new' Stakeholder exists already, query it.
                            # The problem is that the known version here
                            # (old_sh_db.version) is only the one the new
                            # (involved) version is based upon. It is therefore
                            # necessary to also find out the new version and
                            # use a little trick by telling the stakeholder it
                            # actually is this 'new' version.

                            # Query the version this changeset created
                            changeset_part = str(
                                self._convert_utf8(inv_change))
                            created_version = self.Session.query(
                                Stakeholder.version
                            ). \
                                join(Changeset). \
                                filter(
                                Stakeholder.identifier
                                == old_sh_db.stakeholder_identifier). \
                                filter(
                                Stakeholder.previous_version
                                == old_sh_db.version). \
                                filter(
                                Changeset.diff.contains(changeset_part)). \
                                first()

                            if created_version is not None:
                                sh = sp.read_one_by_version(
                                    request,
                                    old_sh_db.stakeholder_identifier,
                                    old_sh_db.version
                                )

                                # Nasty little hack
                                sh._version = created_version.version

                                new_version.add_involvement(Inv(
                                    sh.get_guid(),
                                    sh,
                                    role_db.name,
                                    role_db.id,
                                    created_version.version,
                                    sh.get_status_id()
                                ))

        # Also push Stakeholders where involvements were deleted to new version
        if implicit is not True:
            for i, a in enumerate(swdi_id):
                # Query database
                old_sh_db = self.Session.query(Stakeholder). \
                    filter(Stakeholder.stakeholder_identifier == a). \
                    filter(Stakeholder.version == swdi_version[i]). \
                    first()
                if db is True:
                    # Push Stakeholder to new version
                    # Simulate a dict
                    sh_dict = {
                        'id': old_sh_db.stakeholder_identifier,
                        'version': old_sh_db.version,
                        'activities': [{
                            'op': 'delete',
                            'id': old_version.activity_identifier,
                            'version': swdi_version[i],
                            'role': swdi_role[i]
                        }],
                        'implicit_involvement_update': True
                    }
                    if db_object is not None:
                        new_sh = db_object
                    else:
                        new_sh, new_diff = sp._handle_stakeholder(
                            request, sh_dict, changeset
                        )
                else:
                    # TODO
                    raise Exception('This still needs to be implemented.')
