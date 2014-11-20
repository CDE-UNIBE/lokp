import datetime
import geojson
import json
import logging
import uuid
from geoalchemy import WKBSpatialElement
from geoalchemy.functions import functions as geofunctions
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPNotFound
from pyramid.i18n import get_localizer
from pyramid.security import (
    authenticated_userid,
    effective_principals,
)
from shapely import wkb
from shapely.geometry import asShape
from shapely.geometry.polygon import Polygon
from sqlalchemy import (
    func,
    distinct,
)
from sqlalchemy.sql.expression import (
    and_,
    asc,
    cast,
    desc,
    not_,
    or_,
    select,
)
from sqlalchemy.types import Float

from lmkp.models.database_objects import (
    A_Key,
    A_Value,
    A_Tag,
    A_Tag_Group,
    Activity,
    Changeset,
    Institution,
    Involvement,
    Language,
    Profile,
    Stakeholder,
    Stakeholder_Role,
    Status,
    User,
)
from lmkp.utils import validate_bbox
from lmkp.views.form_config import getCategoryList
from lmkp.views.protocol import (
    Feature,
    Inv,
    # Protocol,
    Tag,
    TagGroup,
)
from lmkp.views.translation import get_translated_status
from lmkp.views.translation import get_translated_db_keys
from lmkp.views.translation import statusMap
from lmkp.views.views import (
    get_bbox_parameters,
    get_current_profile,
    get_current_logical_filter_operator,
    get_status_parameter,
    get_current_order_direction,
)
from lmkp.authentication import get_user_privileges
from lmkp.protocols.protocol import Protocol
from lmkp.models.meta import DBSession as Session


class ActivityFeature3(Feature):
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
        geometry = None
        try:
            geom = wkb.loads(str(self._geometry.geom_wkb))
            geometry = json.loads(geojson.dumps(geom))
        except AttributeError:
            pass
        if isinstance(self._geometry, geojson.geometry.Point):
            geometry = json.loads(geojson.dumps(self._geometry))
        return geometry

    def to_table(self, request):
        """
        Returns a JSON compatible representation of this object
        """

        # Tag Groups
        tg = []
        for t in self._taggroups:
            tg.append(t.to_table())

        # Geometry
        geometry = None
        try:
            geom = wkb.loads(str(self._geometry.geom_wkb))
            geometry = json.loads(geojson.dumps(geom))
        except AttributeError:
            pass

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

    def __init__(self, request):
        self.Session = Session
        self.request = request

    # TODO: request not necessary
    def read_many(self, request, public=True, **kwargs):
        """
        Valid kwargs:
        - limit
        - offset
        """

        relevant_activities = self.get_relevant_activities_many(
            public_query=public)

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

    def get_relevant_activities_many(
            self, filter=None, public_query=False, bbox_cookies=True):
        """
        ''filter'': An optional custom filter.
        ''public_query'': If set to true, no pending queries are made. Defaults
          to 'False'
        """
        logged_in, is_moderator = get_user_privileges(self.request)

        # TODO
        # Filter: If no custom filter was provided, get filters from request
        if filter is None:
            a_tag_filters, sh_tag_filters = self.get_attribute_filters()
        else:
            status_filter = (filter['status_filter']
                             if 'status_filter' in filter else None)
            # TODO: Rename (make sure the filters passed from other
            # protocol are handled correctly)
            a_tag_filters = (
                filter['a_tag_filter'] if 'a_tag_filter' in filter else None)
            sh_tag_filters = (
                filter['sh_tag_filter'] if 'sh_tag_filter' in filter else None)

        # Prepare order: Get the order from request
        order_query = self.get_order('a')

        # Create relevant Activities
        relevant_activities = self.Session.query(
            Activity.id.label('order_id'),
            order_query.c.value.label('order_value'),
            Activity.fk_status,
            Activity.activity_identifier
        )

        # Add a status filter if there is one set
        if get_status_parameter(self.request) is not None:
            relevant_activities = relevant_activities.\
                filter(self.get_status_filter(Activity))

        # Activity attribute filters
        filter_subquery = None
        if len(a_tag_filters) == 0:
            pass
        elif get_current_logical_filter_operator(self.request) == 'or':
            """
            Logical "or" filter: Use subqueries to collect the IDs of
            all Activities matching each filter. Perform a SQL UNION
            based on the first subquery to unite all other subqueries
            and put all Activity IDs together.
            """
            subqueries = []
            for tag_filter in a_tag_filters:
                tag_filter_subquery = tag_filter.subquery()
                subquery = self.Session.query(
                    Activity.id.label('a_filter_id')
                ).\
                    join(A_Tag_Group).\
                    join(tag_filter_subquery,
                         tag_filter_subquery.c.a_filter_tg_id
                         == A_Tag_Group.id)
                subqueries.append(subquery)
            filter_subquery = subqueries[0].union(* subqueries[1:]).subquery()
        else:
            """
            Logical "and" filter: Create a subquery by joining every
            filter subquery.
            """
            filter_subquery = self.Session.query(
                Activity.id.label('a_filter_id')
            )
            for tag_filter in a_tag_filters:
                tag_filter_subquery = tag_filter.subquery()
                subquery = self.Session.query(
                    Activity.id.label('a_filter_id')
                ).\
                    join(A_Tag_Group).\
                    join(tag_filter_subquery,
                         tag_filter_subquery.c.a_filter_tg_id
                         == A_Tag_Group.id).\
                    subquery()
                filter_subquery = filter_subquery.\
                    join(subquery, subquery.c.a_filter_id == Activity.id)
            filter_subquery = filter_subquery.subquery()

        # Join Activities with TagGroups
        if filter_subquery is not None:
            # If a filter was provided, join with filtered subqueries
            relevant_activities = relevant_activities.\
                join(filter_subquery,
                     filter_subquery.c.a_filter_id == Activity.id)
        else:
            # If no filter was provided, simply join with A_Tag_Group (outer
            # join to also capture empty Items)
            relevant_activities = relevant_activities.\
                outerjoin(A_Tag_Group)

        # Always filter by profile boundary
        relevant_activities = relevant_activities.\
            filter(self.get_profile_filter())

        # Filter spatially
        relevant_activities = relevant_activities.\
            filter(self.get_bbox_filter(cookies=bbox_cookies))

        # Join Activities with order and group
        relevant_activities = relevant_activities.\
            outerjoin(order_query, order_query.c.id == Activity.id)

        # Decide which version a user can see.
        # - Public (not logged in) always see active versions.
        # - Logged in users see their own pending versions, as long as they are
        #   newer than the active version.
        # - Moderators see their own and other pending versions if they are
        #   within their profile, as long as they are newer than the active
        #   version.

        # Add pending Activities if allowed and available
        if logged_in and public_query is False:
            """
            Find the latest visible version for each Activity. By
            default, this is the active version. It is the pending
            version if the changes were made by the current user. Or it
            is the pending version if the current user is moderator and
            the version lies within the moderator's profile.
            """
            visible_version_filters = [
                Activity.fk_status == 2,
                and_(
                    Activity.fk_status == 1,
                    Changeset.fk_user == self.request.user.id
                )
            ]
            if is_moderator:
                visible_version_filters.append(
                    and_(
                        Activity.fk_status == 1,
                        self._get_spatial_moderator_filter(self.request)
                    )
                )

            latest_visible_version = self.Session.query(
                Activity.activity_identifier.label('identifier'),
                func.max(Activity.version).label('max_version')
            ).\
                join(Changeset).\
                filter(or_(* visible_version_filters)).\
                group_by(Activity.identifier).\
                subquery()

            relevant_activities = relevant_activities.\
                join(latest_visible_version, and_(
                    latest_visible_version.c.identifier == Activity.identifier,
                    latest_visible_version.c.max_version == Activity.version
                ))

        else:
            # Public (not logged in): show only active
            # TODO: make this more dynamic?
            relevant_activities = relevant_activities.\
                filter(Activity.fk_status == 2)

        relevant_activities = relevant_activities.\
            group_by(Activity.id, order_query.c.value, Activity.fk_status,
                     Activity.activity_identifier)

        # Filter based on Stakeholder attributes
        if len(sh_tag_filters) > 0:
            TODO
            # Prepare a dict to simulate filter for Stakeholders
            sh_filter_dict = {
                'sh_tag_filter': sh_tag_filters,
                'sh_filter_length': len(sh_tag_filters),
                'status_filter': status_filter
            }
            # Use StakeholderProtocol to query id's of Stakeholders
            from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
            sp = StakeholderProtocol3(self.Session)
            rel_sh = sp._get_relevant_stakeholders_many(
                self.request, filter=sh_filter_dict)
            sh_query = sp._query_only_id(rel_sh)
            sh_subquery = sh_query.subquery()
            if self._get_logical_operator(self.request) == 'or':
                # OR: use 'union' to add id's to relevant_activities
                relevant_activities = relevant_activities.\
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
                relevant_activities = relevant_activities.\
                    join(Involvement).\
                    join(sh_subquery, sh_subquery.c.id ==
                         Involvement.fk_stakeholder).\
                    group_by(Activity.id)

        # Do the ordering
        if get_current_order_direction(self.request) == 'desc':
            relevant_activities = relevant_activities.order_by(
                desc(order_query.c.value))
        else:
            relevant_activities = relevant_activities.order_by(
                asc(order_query.c.value))

        return relevant_activities

    def _query_many(
            self, request, relevant_activities, limit=None, offset=None,
            involvements=False, return_count=True, metadata=False):
        # Prepare query to translate keys and values
        localizer = get_localizer(request)
        lang = self.Session.query(
            Language
        ).\
            filter(Language.locale == localizer.locale_name).\
            first()
        key_translation, value_translation = self._get_translatedKV(
            lang, A_Key, A_Value
        )

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
        ).\
            join(relevant_activities,
                 relevant_activities.c.order_id == Activity.id).\
            join(Status).\
            join(Changeset).\
            outerjoin(A_Tag_Group).\
            outerjoin(A_Tag, A_Tag_Group.id == A_Tag.fk_a_tag_group).\
            outerjoin(A_Key).\
            outerjoin(A_Value, A_Tag.fk_value == A_Value.id).\
            outerjoin(key_translation,
                      key_translation.c.key_original_id == A_Key.id).\
            outerjoin(value_translation,
                      value_translation.c.value_original_id == A_Value.id)

        # Do the ordering again: A first ordering was done when creating the
        # relevant activities. However, it is necessary to restore this
        # ordering after all the additional data was added through this query.
        if get_current_order_direction(request) == 'desc':
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
            ).\
                outerjoin(User, User.id == Changeset.fk_user).\
                outerjoin(Institution)

        if involvements:
            inv_status_filter = self.Session.query(
                Status.id
            ).\
                filter(or_(* self._get_involvement_status(request)))

            # Additional filter to select only the latest (pending or not)
            # Stakeholder involved with the relevant Activities
            latest_filter = self.Session.query(
                Stakeholder.stakeholder_identifier,
                Involvement.fk_activity,
                func.max(Stakeholder.version).label('max_version')
            ).\
                join(Involvement).\
                join(relevant_activities, relevant_activities.c.order_id ==
                     Involvement.fk_activity).\
                group_by(Stakeholder.stakeholder_identifier,
                         Involvement.fk_activity).\
                subquery()

            inv_status = self.Session.query(
                Stakeholder.id.label('stakeholder_id'),
                Stakeholder.stakeholder_identifier.
                label('stakeholder_identifier'),
                Stakeholder.fk_status.label('stakeholder_status'),
                Stakeholder.version.label('stakeholder_version'),
                Stakeholder.fk_changeset.label('changeset_id')
            ).\
                filter(Stakeholder.fk_status.in_(inv_status_filter)).\
                join(Involvement).\
                join(latest_filter, and_(
                    latest_filter.c.max_version == Stakeholder.version,
                    latest_filter.c.stakeholder_identifier
                    == Stakeholder.stakeholder_identifier,
                    latest_filter.c.fk_activity == Involvement.fk_activity
                )).\
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
            ).\
                join(inv_status, inv_status.c.stakeholder_id ==
                     Involvement.fk_stakeholder).\
                join(Changeset, Changeset.id == inv_status.c.changeset_id).\
                join(Stakeholder_Role).\
                subquery()

            #log.debug("Involvement Query:\n%s" % inv_query)

            query = query.\
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
                ).\
                outerjoin(inv_query, inv_query.c.activity_id == Activity.id)

        if return_count:
            return query, count
        else:
            return query

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

                activity = ActivityFeature3(
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
                                        and p_i.get_status() == 1):
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
            from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
            sp = StakeholderProtocol3(self.Session)
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

    def get_profile_filter(self):
        """
        Return an GeoAlchemy filter expression based on the profile
        boundary of the current profile. If no profile is active, a stub
        expression is returned filtering nothing.

        .. seealso::
           :class:`lmkp.views.views.get_current_profile`

        Returns:
            ``sqlalchemy.sql.expression``. A GeoAlchemy expression which
            can be used as a filter on the :term:`Activity` point
            geometry.
        """
        profile = self.Session.query(Profile).\
            filter(Profile.code == get_current_profile(self.request)).\
            first()
        if profile is None:
            return (Activity.id == 0)
        return geofunctions.intersects(Activity.point, profile.geometry)

    def get_bbox_filter(self, cookies=True):
        """
        Return a spatial filter for the point of Activities based on the
        bounding box parameters found in the request.

        If a valid bounding box was found, a GeoAlchemy function
        intersecting the point geometries of Activities with the
        bounding box geometry is returned. This function can then be
        used as a filter in SQLAlchemy.

        Kwargs:
            ``cookies`` (bool): A boolean indicating whether to look for
            a location cookie as fallback if no request parameters were
            provided. This argument is passed to the
            `get_bbox_parameters` function.

            .. seealso::
               :class:`lmkp.views.views.get_bbox_parameters`

        Returns:
            ``geoalchemy.functions.intersects`` or ``None``. A
            GeoAlchemy function which intersects the points of
            Activities with the bounding box geometry. None if no valid
            bounding box was found.
        """
        bbox, epsg = get_bbox_parameters(self.request, cookies=cookies)
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
        wkb_geometry = WKBSpatialElement(
            buffer(geometry.wkb), epsg)

        # Get the SRID used in the Activity class
        activity_srid = geofunctions.srid(Activity.point)

        return geofunctions.intersects(
            Activity.point,
            geofunctions.transform(wkb_geometry, activity_srid))

    def _get_spatial_moderator_filter(self, request):
        """
        Create an array of geometry filters based on the user's profile(s)
        """
        userid = request.user.username  # authenticated_userid(request)

        profile_filters = []

        if userid is not None:
            profiles = self.Session.query(Profile).\
                filter(Profile.users.any(username=userid))
            for p in profiles.all():
                profile_filters.append(geofunctions.intersects(Activity.point,
                                       p.geometry))
                if p.code == 'global':
                    profile_filters.append(Activity.point == None)

        if len(profile_filters) > 0:
            return or_(* profile_filters)

        return None
