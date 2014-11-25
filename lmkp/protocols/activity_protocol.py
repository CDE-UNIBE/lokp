import geojson
import json
from geoalchemy import WKBSpatialElement
from geoalchemy.functions import functions as geofunctions
from pyramid.security import (
    authenticated_userid,
    effective_principals,
)
from shapely import wkb
from shapely.geometry.polygon import Polygon
from sqlalchemy import (
    func,
)
from sqlalchemy.sql.expression import (
    and_,
    asc,
    cast,
    desc,
    not_,
    or_,
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
    # Feature,
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
    get_current_involvement_details,
    get_current_limit,
    get_current_offset,
)
from lmkp.authentication import get_user_privileges
from lmkp.protocols.protocol import Protocol
from lmkp.models.meta import DBSession as Session
from lmkp.protocols.activity_feature import ActivityFeature


class ActivityProtocol(Protocol):
    """
    TODO
    """

    def __init__(self, request):
        self.Session = Session
        self.request = request

    # TODO: request not necessary
    def read_many(self, public=True, limit=None, offset=None, translate=True):
        """
        Valid kwargs:
        - limit
        - offset
        - translate
        """

        relevant_activities = self.get_relevant_activities_many(
            public_query=public)

        involvement_details = get_current_involvement_details(self.request)
        show_involvements = involvement_details != 'none'

        if limit is None:
            limit = get_current_limit(self.request)
        if offset is None:
            offset = get_current_offset(self.request)

        query, count = self.query_many(
            relevant_activities, limit=limit, offset=offset,
            with_involvements=show_involvements)

        activities = self.query_to_activities(
            query, involvements=involvement_details, public_query=public,
            translate=translate)

        return {
            'total': count,
            'data': [a.to_table(self.request) for a in activities]
        }

    def get_relevant_activities_many(
            self, filter=None, public_query=False, bbox_cookies=True):
        """
        Get the relevant activities (mainly their IDs) based on the
        various filters (attributes on both :term:`Activities` and
        :term:`Stakeholders`, :term:`Status`, :term:`Profile` etc.)
        which are currently set.

        Args:
            ``filter`` (dict): An optional dictionary with custom
            filters, overwriting the ones from the request. (TODO)

            ``public_query`` (bool): An optional boolean indicating
            whether to return only versions visible to the public (eg.
            no pending) or not.

            ``bbox_cookies`` (bool): An optional boolean indicating
            whether to look for a location cookie as fallback if no
            request parameters were provided. This argument is passed to
            the `get_bbox_parameters` function.

            .. seealso::
               :class:`lmkp.views.views.get_bbox_parameters`

        Returns:
            ``sqlalchemy.orm.query.Query``. A SQLAlchemy Query
            containing namely the IDs of the filtered (relevant)
            :term:`Activities`.
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

        # Decide which version is based on status filter and user
        # privileges.
        relevant_activities = self.apply_visible_version_filter(
            'a', relevant_activities, public_query=public_query)

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

    def query_many(
            self, relevant_activities, limit=None, offset=None,
            with_involvements=False, return_count=True,
            with_metadata=False):
        """
        Get a complete query object for some relevant
        :term:`Activities`. This does not actually perform a query
        (except a SQL count if requested) but rather creates and returns
        a query joining the relevant :term:`Activities` with all its
        attributes and involvements.

        Args:
            ``relevant_activities`` (sqlalchemy.orm.query.Query): A
            SQLAlchemy containing the filtered (relevant)
            :term:`Activities`.

            .. seealso::
               :class:`get_relevant_activities_many`

            ``limit`` (int or None): An optional integer with the limit
            to be applied to the query.

            ``offset`` (int or None): An optional integer with the
            offset to be applied to the query.

            ``with_involvements`` (bool): An optional boolean indicating
            whether to include :term:`Involvements` in the query or not.
            If true, additional columns for the attributes of the
            :term:`Stakeholders` are added to the query. Defaults to
            ``false``.

            ``return_count`` (bool): An optional boolean indicating
            whether to return the count of the query along with the
            query. The count happens before the limit and offset are
            applied, it therefore returns the total count of the entire
            query. Defaults to ``true``.

            ``with_metadata`` (bool): An optional boolean indicating
            whether to include metadata (eg. about the user and
            institution creating the version) for the :term:`Activities`
            or not. Defaults to ``false``.

        Returns:
            ``sqlalchemy.orm.query.Query``. A SQLAlchemy Query for the
            :term:`Activities`.

            ``long``. (only if ``return_count=True``) The total count of
            the query.
        """
        key_translation, value_translation = self.get_translation_queries('a')

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
        if get_current_order_direction(self.request) == 'desc':
            query = query.order_by(desc(relevant_activities.c.order_value))
        else:
            query = query.order_by(asc(relevant_activities.c.order_value))

        if with_metadata is True:
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

        if with_involvements is True:
            logged_in, is_moderator = get_user_privileges(self.request)
            involvement_status_ids = self.get_valid_status_ids(
                'involvements', logged_in, is_moderator)

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
                filter(Stakeholder.fk_status.in_(involvement_status_ids)).\
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

    def query_to_activities(
            self, query, involvements='none', public_query=False,
            with_taggroup_geometry=False, translate=True, **kwargs):
        """
        Every value of each :term:`Activity` is a line of the query.
        These attributes have to be collected to form a ActivityFeature.
        """

        logged_in, is_moderator = get_user_privileges(self.request)

        if with_taggroup_geometry is True:
            query = query.add_columns(
                A_Tag_Group.geometry.label('tg_geometry')
            )

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
                if (with_taggroup_geometry is True
                        and q.tg_geometry is not None):
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
                            request_user_id = self.request.user.id
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
                self.request, inv_dicts)

            sh_query = sp._query_many(
                self.request, relevant_stakeholders, involvements=False,
                return_count=False)
            stakeholders = sp._query_to_stakeholders(
                self.request, sh_query, involvements='none')

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
        Return a spatial filter for the point of :term:`Activities`
        based on the bounding box parameters found in the request.

        If a valid bounding box was found, a GeoAlchemy function
        intersecting the point geometries of Activities with the
        bounding box geometry is returned. This function can then be
        used as a filter in SQLAlchemy.

        Args:
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

    def get_user_spatial_profile_filter(self):
        """
        Return the spatial filters for the point of :term:`Activities`
        based on the profile(s) associated with the current user. If the
        user has multiple profiles, the spatial filters for each profile
        are connected with a SQL ``OR`` statement.

        Returns:
            ``geoalchemy.functions.intersects`` or
            ``sqlalchemy.sql.expression`` or ``None``. A GeoAlchemy
            function or multiple joined in a SQLAlchemy expression.
        """
        userid = authenticated_userid(self.request)

        profile_filters = []
        if userid is not None:
            profiles = self.Session.query(Profile).\
                filter(Profile.users.any(username=userid))
            for p in profiles.all():
                profile_filters.append(
                    geofunctions.intersects(Activity.point, p.geometry))
                if p.code == 'global':
                    profile_filters.append(Activity.point == None)

        if len(profile_filters) > 0:
            return or_(* profile_filters)

        return None
