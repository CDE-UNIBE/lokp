import logging

import uuid
import simplejson as json

from lmkp.models.database_objects import *
from lmkp.views.protocol import *
from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
from lmkp.views.translation import statusMap
from lmkp.views.translation import get_translated_status

from geoalchemy import WKBSpatialElement
from geoalchemy.functions import functions
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.i18n import get_localizer
from pyramid.security import authenticated_userid
from shapely.geometry import asShape
from shapely.geometry.polygon import Polygon
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.expression import asc
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql.expression import or_
from sqlalchemy.sql.expression import not_
from sqlalchemy.sql.expression import select


log = logging.getLogger(__name__)

class ActivityFeature3(Feature):
    """
    Overwrites the super class Feature and adds the geometry property
    """

    def __init__(self, guid, order_value, geometry=None, version=None,
        status=None, status_id=None, timestamp=None):
        self._taggroups = []
        self._involvements = []
        self._guid = guid
        self._order_value = order_value
        self._geometry = geometry
        self._version = version
        self._status = status
        self._status_id = status_id
        self._timestamp = timestamp

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
            geometry = {}
            geometry['type'] = 'Point'
            geometry['coordinates'] = [geom.x, geom.y]
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

        # Involvements
        if len(self._involvements) != 0:
            sh = []
            for i in self._involvements:
                sh.append(i.to_table(request))
            ret['involvements'] = sh

        return ret

class ActivityProtocol3(Protocol):

    def __init__(self, Session):
        self.Session = Session

    def create(self, request, data=None):
        """
        Create or update Activities
        """

        diff = request.json_body if data is None else data

        user = self.Session.query(User).\
            filter(User.username == authenticated_userid(request)).\
            first()

        # Changeset
        changeset = Changeset()
        changeset.user = user

        # Check if the json body is a valid diff file
        if 'activities' not in diff:
            raise HTTPBadRequest(detail="Not a valid format")

        # Get the current configuration file to validate key and value pairs
        self.configuration = self._read_configuration(request, 'activity.yml')

        # Return the IDs of the newly created Activities
        ids = []
        for activity in diff['activities']:
            
            a = self._handle_activity(request, activity, changeset)

            # Add the newly created identifier to the diff
            activity[unicode('id')] = unicode(a.activity_identifier)

            ids.append(a)

        # Save diff to changeset and handle UTF-8 of diff
        changeset.diff = str(self._convert_utf8(diff))

        return ids

    def read_one_active(self, request, uid):

        relevant_activities = self._get_relevant_activities_one_active(uid)

        # Determine if and how detailed Involvements are to be displayed.
        # Default is: 'full'
        inv_details = request.params.get('involvements', 'full')

        query, count = self._query_many(request, relevant_activities,
            involvements=inv_details!='none')

        activities = self._query_to_activities(request, query,
            involvements=inv_details, public_query=True)

        return {
            'total': count,
            'data': [a.to_table(request) for a in activities]
        }

    def read_one_by_version(self, request, uid, version=None):

        relevant_activities = self._get_relevant_activities_one_by_version(uid, version)

        # Determine if and how detailed Involvements are to be displayed.
        # Default is: 'full'
        inv_details = request.params.get('involvements', 'full')

        query, count = self._query_many(request, relevant_activities,
            involvements=inv_details!='none')

        activities = self._query_to_activities(request, query,
            involvements=inv_details, public_query=True)

        return activities[0]


    def read_one(self, request, uid, public=True):

        relevant_activities = self._get_relevant_activities_one(request, uid,
            public_query=public)

        # Determine if and how detailed Involvements are to be displayed.
        # Default is: 'full'
        inv_details = request.params.get('involvements', 'full')

        # Get limit and offset from request.
        # Defaults: limit = None / offset = 0
        limit = self._get_limit(request)
        offset = self._get_offset(request)

        query, count = self._query_many(request, relevant_activities,
            limit=limit, offset=offset, involvements=inv_details!='none')

        # Order the Activity by version
        query = query.order_by(desc(Activity.version))

        activities = self._query_to_activities(request, query,
            involvements=inv_details, public_query=public)

        return {
            'total': count,
            'data': [a.to_table(request) for a in activities]
        }

    def read_many(self, request, public=True):

        relevant_activities = self._get_relevant_activities_many(
            request, public_query=public)

        # Determine if and how detailed Involvements are to be displayed.
        # Default is: 'full'
        inv_details = request.params.get('involvements', 'full')

        # Get limit and offset from request.
        # Defaults: limit = None / offset = 0
        limit = self._get_limit(request)
        offset = self._get_offset(request)

        query, count = self._query_many(
            request, relevant_activities, limit=limit, offset=offset,
            involvements=inv_details!='none')

        activities = self._query_to_activities(
            request, query, involvements=inv_details, public_query=public)

        return {
            'total': count,
            'data': [a.to_table(request) for a in activities]
        }

    def read_many_by_stakeholder(self, request, uid, public=True):

        relevant_activities = self._get_relevant_activities_by_stakeholder(
            request, uid, public_query=public)

        # Determine if and how detailed Involvements are to be displayed.
        # Default is: 'full'
        inv_details = request.params.get('involvements', 'full')

        # Get limit and offset from request.
        # Defaults: limit = None / offset = 0
        limit = self._get_limit(request)
        offset = self._get_offset(request)

        query, count = self._query_many(
            request, relevant_activities, limit=limit, offset=offset,
            involvements=inv_details!='none')

        activities = self._query_to_activities(
            request, query, involvements=inv_details, public_query=public)

        return {
            'total': count,
            'data': [a.to_table(request) for a in activities]
        }

    def read_many_geojson(self, request, public=True):

        relevant_activities = self._get_relevant_activities_many(
            request, public_query=public)

        # Get limit and offset from request.
        # Defaults: limit = None / offset = 0
        limit = self._get_limit(request)
        offset = self._get_offset(request)

        query = self._query_geojson(relevant_activities, limit=limit,
            offset=offset)

        return self._query_to_geojson(query)

    def _get_relevant_activities_one_by_version(self, uid, version):
        # Create relevant Activities
        relevant_activities = self.Session.query(
                Activity.id.label('order_id'),
                func.char_length('').label('order_value'),
                Activity.fk_status,
                Activity.activity_identifier
            ).\
            outerjoin(A_Tag_Group).\
            filter(Activity.activity_identifier == uid).\
            filter(Activity.version == version).\
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
            ).\
            outerjoin(A_Tag_Group).\
            filter(Activity.activity_identifier == uid).\
            filter(Activity.fk_status == 2).\
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
                func.char_length('').label('value') # Dummy value
            ).\
            subquery()

        # Prepare status filter
        status_filter = self.Session.query(
                Status.id
            ).\
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
        relevant_activities = relevant_activities.\
            filter(Activity.activity_identifier == uid)

        # Status filter
        relevant_activities = relevant_activities.\
            filter(Activity.fk_status.in_(status_filter))

        relevant_activities = relevant_activities.\
            outerjoin(A_Tag_Group).\
            outerjoin(order_query, order_query.c.id == Activity.id)

        # If logged in and it is not a public query, add pending versions by
        # current user to selection. This is not necessary for moderators
        # because they already see all pending versions
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

            pending_activities = pending_activities.\
                join(Changeset).\
                filter(Activity.activity_identifier == uid).\
                filter(Activity.fk_status == 1).\
                filter(Changeset.fk_user == request_user_id)

            pending_activities = pending_activities.\
                outerjoin(A_Tag_Group).\
                outerjoin(order_query, order_query.c.id == Activity.id)

            relevant_activities = pending_activities.union(relevant_activities)

        # Join Activities with Tag Groups and order_query, then group it
        relevant_activities = relevant_activities.\
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
            request, Activity, A_Tag_Group, A_Tag, A_Key, A_Value
        )
        
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
        relevant_activities = relevant_activities.\
            outerjoin(A_Tag_Group).\
            outerjoin(order_query, order_query.c.id == Activity.id).\
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

    def _get_relevant_activities_many(self, request, filter=None,
        public_query=False):
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
                ).\
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
                    ).\
                    join(A_Tag_Group).\
                    join(taggroups_sq,
                        taggroups_sq.c.a_filter_tg_id == A_Tag_Group.id)
                all_subqueries.append(single_subquery)
            # Put all found Activity IDs together (UNION)
            filter_subqueries = all_subqueries[0].\
                union(* all_subqueries[1:]).\
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
                    ).\
                    join(A_Tag_Group).\
                    join(taggroups_sq,
                        taggroups_sq.c.a_filter_tg_id == A_Tag_Group.id).\
                    subquery()
                # Join each found Activity ID with previously found IDs
                filter_subqueries = filter_subqueries.\
                    join(single_subquery,
                        single_subquery.c.a_filter_id == Activity.id)
            filter_subqueries = filter_subqueries.subquery()

        # Prepare order: Get the order from request
        order_query, order_numbers = self._get_order(
            request, Activity, A_Tag_Group, A_Tag, A_Key, A_Value
        )

        # Create relevant Activities
        relevant_activities = self.Session.query(
            Activity.id.label('order_id'),
            order_query.c.value.label('order_value'),
            Activity.fk_status,
            Activity.activity_identifier
        )

        # Join Activities with TagGroups
        if filter_subqueries is not None:
            # If a filter was provided, join with filtered subqueries
            relevant_activities = relevant_activities.\
                join(filter_subqueries,
                    filter_subqueries.c.a_filter_id == Activity.id)
        else:
            # If no filter was provided, simply join with A_Tag_Group (outer
            # join to also capture empty Items)
            relevant_activities = relevant_activities.\
                outerjoin(A_Tag_Group)

        # Filter spatially
        relevant_activities = relevant_activities.\
            filter(self._get_bbox_filter(request))

        # Join Activities with order and group
        relevant_activities = relevant_activities.\
            outerjoin(order_query, order_query.c.id == Activity.id)

        # Filter by timestamp
        # @TODO: do it!
        timestamp_filter = None

        # Apply status filter (only if timestamp filter is not set)
        if status_filter is not None and timestamp_filter is None:
            relevant_activities = relevant_activities.\
                filter(Activity.fk_status.in_(status_filter))

        # If logged in and it is not a public query, add pending versions by
        # current user to selection. If moderator, add all pending versions
        # which are within user's profile(s) and within spatial extent.
        if logged_in and public_query is False:

            # It is necessary to first find out if there are Activities pending
            # and if yes, which is the latest version
            latest_pending_activities = self.Session.query(
                    Activity.activity_identifier,
                    func.max(Activity.version).label('max_version')
                ).\
                join(Changeset).\
                filter(Activity.fk_status == 1)

            if not is_moderator:
                # If current user is not a moderator, only show pending versions
                # done by himself
                latest_pending_activities = latest_pending_activities.\
                    filter(Changeset.fk_user == request.user.id)

            latest_pending_activities = latest_pending_activities.\
                group_by(Activity.activity_identifier).\
                subquery()

            # Collect other information about pending Activities (order, ...)
            pending_activities = self.Session.query(
                    Activity.id.label('order_id'),
                    order_query.c.value.label('order_value'),
                    Activity.fk_status,
                    Activity.activity_identifier
                ).\
                join(latest_pending_activities, and_(
                    latest_pending_activities.c.max_version == Activity.version,
                    latest_pending_activities.c.activity_identifier
                        == Activity.activity_identifier
                ))

            # Join pending Activities with TagGroups and filters to find out if
            # they are to be displayed at all
            if filter_subqueries is not None:
                # If a filter was provided, join with filtered subqueries
                pending_activities = pending_activities.\
                    join(filter_subqueries,
                        filter_subqueries.c.a_filter_id == Activity.id)
            else:
                # If no filter was provided, simply join with A_Tag_Group (outer
                # join to also capture empty Items)
                pending_activities = pending_activities.\
                    outerjoin(A_Tag_Group)

            # Filter spatially
            pending_activities = pending_activities.\
                filter(self._get_bbox_filter(request))

            # If moderator, also filter by his profile extents.
            # @TODO: This also filters out pending versions done by himself
            # which are not in his profiles but in the current view. This
            # could/should be corrected.
            if is_moderator:
                pending_activities = pending_activities.\
                    filter(self._get_spatial_moderator_filter(request))

            # Join pending Activities with order and group
            pending_activities = pending_activities.\
                outerjoin(order_query, order_query.c.id == Activity.id).\
                group_by(Activity.activity_identifier, Activity.id,
                    order_query.c.value)

            # Filter out the active Activities if they have a pending version.
            # Then union with pending Activities.
            relevant_activities = relevant_activities.filter(
                not_(Activity.activity_identifier.in_(
                    select([pending_activities.\
                        subquery().c.activity_identifier])
                ))
            )
            relevant_activities = pending_activities.union(relevant_activities)

        relevant_activities = relevant_activities.\
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
            sp = StakeholderProtocol3(self.Session)
            rel_sh = sp._get_relevant_stakeholders_many(
                request, filter=sh_filter_dict)
            sh_query = sp._query_only_id(rel_sh)
            sh_subquery = sh_query.subquery()
            if self._get_logical_operator(request) == 'or':
                # OR: use 'union' to add id's to relevant_activities
                relevant_activities = relevant_activities.\
                    union(self.Session.query(
                            Activity.id.label('order_id'),
                            func.char_length('').label('order_value'), # dummy
                            Activity.fk_status,
                            Activity.activity_identifier
                        ).\
                        join(Involvement).\
                        join(sh_subquery, sh_subquery.c.id ==
                            Involvement.fk_stakeholder).\
                        group_by(Activity.id))
            else:
                # AND: filter id's of relevant_activities
                relevant_activities = relevant_activities.\
                    join(Involvement).\
                    join(sh_subquery, sh_subquery.c.id ==
                         Involvement.fk_stakeholder).\
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

    def _get_relevant_activities_by_stakeholder(self, request, uid,
        public_query=False):

        logged_in, is_moderator = self._get_user_status(
            effective_principals(request))

        # Use StakeholderProtocol to query the Stakeholder versions
        # corresponding to given uid
        sp = StakeholderProtocol3(self.Session)
        relevant_stakeholders = sp._get_relevant_stakeholders_one(request,
            uid=uid, public_query=public_query)

        # Always take the latest one.
        relevant_stakeholders = relevant_stakeholders.\
            limit(1).\
            subquery()

        # Prepare status filter
        status_filter = self.Session.query(
                    Status.id
                ).\
                filter(or_(* self._get_status(request)))

        # Prepare order: Get the order from request
        order_query, order_numbers = self._get_order(
            request, Activity, A_Tag_Group, A_Tag, A_Key, A_Value
        )

        # Create relevant Activities
        relevant_activities = self.Session.query(
            Activity.id.label('order_id'),
            order_query.c.value.label('order_value'),
            Activity.fk_status,
            Activity.activity_identifier
        )

        # Filter trough Involvements to only take Activities involved with
        # relevant Stakeholder
        relevant_activities = relevant_activities.\
            join(Involvement).\
            filter(Involvement.fk_stakeholder.in_(
                select([relevant_stakeholders.c.order_id])
            ))

        # Join Activities with Tag Groups and order_query, then group it
        relevant_activities = relevant_activities.\
            outerjoin(A_Tag_Group).\
            outerjoin(order_query, order_query.c.id == Activity.id).\
            filter(Activity.fk_status.in_(status_filter))
            
        # If logged in and it is not a public query, add pending versions by 
        # current user to selection. If moderator, add all pending versions.
        if logged_in and public_query is False:
            
            # It is necessary to first find out, if there are Activities
            # pending and if yes, which is the latest version
            latest_pending_activities = self.Session.query(
                    Activity.activity_identifier,
                    func.max(Activity.version).label('max_version')
                ).\
                join(Changeset).\
                filter(Activity.fk_status == 1)
            
            if not is_moderator:
                # If current user is not a moderator, only show pending versions
                # done by himself
                latest_pending_activities = latest_pending_activities.\
                    filter(Changeset.fk_user == request.user.id)
                
            latest_pending_activities = latest_pending_activities.\
                group_by(Activity.activity_identifier).\
                subquery()

            # Collect other information about pending Activities (order, ...)
            pending_activities = self.Session.query(
                    Activity.id.label('order_id'),
                    order_query.c.value.label('order_value'),
                    Activity.fk_status,
                    Activity.activity_identifier
                ).\
                join(latest_pending_activities, and_(
                    latest_pending_activities.c.max_version
                        == Activity.version,
                    latest_pending_activities.c.activity_identifier
                        == Activity.activity_identifier
                ))

            # Filter trough Involvements to only take Activities involved with
            # relevant Stakeholder
            pending_activities = pending_activities.\
                join(Involvement).\
                filter(Involvement.fk_stakeholder.in_(
                    select([relevant_stakeholders.c.order_id])
                ))

            # Join Activities with Tag Groups and order_query, then group it
            pending_activities = pending_activities.\
                outerjoin(A_Tag_Group).\
                outerjoin(order_query, order_query.c.id == Activity.id).\
                group_by(Activity.activity_identifier, Activity.id,
                    order_query.c.value)

            # Filter out the active Activities if they have a pending version.
            # Then union with pending Activities.
            relevant_activities = relevant_activities.filter(
                not_(Activity.activity_identifier.in_(
                    select([pending_activities.subquery().\
                    c.activity_identifier])
                ))
            )
            relevant_activities = pending_activities.union(
                relevant_activities)

        relevant_activities = relevant_activities.\
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
            ).\
            join(relevant_activities,
                relevant_activities.c.order_id == Stakeholder.id)

        return query

    def _query_many(self, request, relevant_activities, limit=None, offset=None,
        involvements=False, return_count=True):
        # Prepare query to translate keys and values
        localizer = get_localizer(request)
        lang = None if localizer.locale_name == 'en' \
            else self.Session.query(Language).\
                filter(Language.locale == localizer.locale_name).\
                first()
        key_translation, value_translation = self._get_translatedKV(lang, A_Key,
            A_Value)
        
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
            outerjoin(A_Value).\
            outerjoin(key_translation,
                key_translation.c.key_original_id == A_Key.id).\
            outerjoin(value_translation,
                value_translation.c.value_original_id == A_Value.id)

        if involvements:
            inv_status_filter = self.Session.query(
                    Status.id
                ).\
                filter(or_(* self._get_involvement_status(request)))
            inv_status = self.Session.query(
                    Stakeholder.id.label('stakeholder_id'),
                    Stakeholder.stakeholder_identifier.\
                        label('stakeholder_identifier'),
                    Stakeholder.fk_status.label('stakeholder_status'),
                    Stakeholder.version.label('stakeholder_version')
                ).\
                filter(Stakeholder.fk_status.in_(inv_status_filter)).\
                subquery()
            inv_query = self.Session.query(
                    Involvement.fk_activity.label('activity_id'),
                    Stakeholder_Role.id.label('role_id'),
                    Stakeholder_Role.name.label('role_name'),
                    Changeset.fk_user.label('stakeholder_user_id'),
                    inv_status.c.stakeholder_identifier.\
                        label('stakeholder_identifier'),
                    inv_status.c.stakeholder_status.label('stakeholder_status'),
                    inv_status.c.stakeholder_version.\
                        label('stakeholder_version')
                ).\
                join(inv_status,
                    inv_status.c.stakeholder_id == Involvement.fk_stakeholder).\
                join(Changeset, Changeset.id == inv_status.c.stakeholder_id).\
                join(Stakeholder_Role).\
                subquery()

            query = query.\
                add_columns(
                    inv_query.c.stakeholder_identifier.\
                        label('stakeholder_identifier'),
                    inv_query.c.role_name.label('stakeholder_role'),
                    inv_query.c.role_id.label('stakeholder_role_id'),
                    inv_query.c.stakeholder_status.label('stakeholder_status'),
                    inv_query.c.stakeholder_version.\
                        label('stakeholder_version'),
                    inv_query.c.stakeholder_user_id.label('stakeholder_user_id')
                ).\
                outerjoin(inv_query, inv_query.c.activity_id == Activity.id)

        if return_count:
            return query, count
        else:
            return query

    def _query_geojson(self, relevant_activities, limit=None, offset=None):

        # Apply limit and offset
        if limit is not None:
            relevant_activities = relevant_activities.limit(limit)
        if offset is not None:
            relevant_activities = relevant_activities.offset(offset)

        # Create query
        relevant_activities = relevant_activities.subquery()
        query = self.Session.query(
                Activity.id.label('id'),
                Activity.point.label('geometry'),
                Activity.activity_identifier.label('identifier'),
                Activity.version.label('version'),
                Status.id.label('status_id'),
                Status.name.label('status_name')
            ).\
            join(relevant_activities,
                relevant_activities.c.order_id == Activity.id).\
            join(Status)

        return query

    def _query_to_activities(self, request, query, involvements='none',
        public_query=False):

        logged_in, is_moderator = self._get_user_status(
            effective_principals(request))

        # Put the Activities together
        activities = []
        for q in query.all():

            # Prepare values if needed
            identifier = str(q.identifier)
            taggroup_id = int(q.taggroup) if q.taggroup is not None else None
            key = q.key_translated if q.key_translated is not None else q.key
            value = (q.value_translated if q.value_translated is not None else
                q.value)

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

            if activity == None:
                activity = ActivityFeature3(
                    identifier, q.order_value, geometry=q.geometry,
                    version=q.version, status=q.status, status_id=q.status_id,
                    timestamp=q.timestamp
                )
                activities.append(activity)

            # Check if current Tag Group is already present in the Activity
            taggroup = None
            if activity.find_taggroup_by_id(taggroup_id) is not None:
                taggroup = activity.find_taggroup_by_id(taggroup_id)
            else:
                taggroup = TagGroup(taggroup_id, q.tg_id, q.main_tag)
                activity.add_taggroup(taggroup)

            # Because of Involvements, the same Tags appears for each
            # Involvement, so add it only once to TagGroup
            if taggroup is not None and taggroup.get_tag_by_id(q.tag) is None:
                taggroup.add_tag(Tag(q.tag, key, value))

            # Involvements
            if involvements != 'none':
                try:
                    if q.stakeholder_identifier is not None:

                        request_user_id = (request.user.id if request.user is
                            not None else None)

                        # Flag indicating if Involvement to this Activity is not
                        # yet found ('none') or not to be added ('false')
                        inv = self._flag_add_involvement(
                            activity,
                            q.status_id,
                            q.stakeholder_status,
                            q.stakeholder_identifier,
                            q.stakeholder_version,
                            q.stakeholder_user_id,
                            q.stakeholder_role,
                            request_user_id,
                            public_query,
                            logged_in,
                            is_moderator
                        )

                        if inv is None:
                            # Create new Involvement and add it to Activity
                            # Default: only basic information about Involvement
                            activity.add_involvement(
                                Inv(
                                    q.stakeholder_identifier,
                                    None,
                                    q.stakeholder_role,
                                    q.stakeholder_role_id,
                                    q.stakeholder_version,
                                    q.stakeholder_status
                                ))
                except ValueError:
                    pass

        if involvements == 'full':
            # If full involvements are to be shown, collect the identifiers and
            # versions of each Stakeholder and prepare a dict. Query the details
            # (Tag Groups) of these Stakeholders using the ActivityProtocol and
            # replace the existing Involvements. Query them all at once to
            # improve performance.

            inv_dicts = []
            for activity in activities:
                for i in activity._involvements:
                        inv_dicts.append({
                            'identifier': i.get_guid(),
                            'version': i.get_version()
                        })

            # Use StakeholderProtocol to query the details of the Activities
            sp = StakeholderProtocol3(self.Session)
            relevant_stakeholders = sp._get_relevant_stakeholders_dict(
                request, inv_dicts)

            sh_query = sp._query_many(request, relevant_stakeholders,
                involvements=False, return_count=False)
            stakeholders = sp._query_to_stakeholders(request, sh_query,
                involvements='none')

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
                            i.get_guid(),
                            stakeholder,
                            i.get_role(),
                            i.get_role_id(),
                            i.get_version(),
                            i.get_status()
                        )

        return activities

    def _query_to_geojson(self, query):

        def _create_feature(id, g, identifier, status_id, status_name, version):
            """
            Small helper function to create a new Feature
            """
            feature = {}

            geom = wkb.loads(str(g.geom_wkb))
            geometry = {}
            geometry['type'] = 'Point'
            geometry['coordinates'] = [geom.x, geom.y]
            feature['geometry'] = geometry

            properties = {
                'status': status_name,
                'status_id': status_id,
                'activity_identifier': str(identifier),
                'version': int(version)
            }
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
            featureCollection['features'].append(
                _create_feature(
                    q.id,
                    q.geometry,
                    q.identifier,
                    q.status_id,
                    q.status_name,
                    q.version
                )
            )

        return featureCollection

    def _get_spatial_moderator_filter(self, request):
        """
        """
        userid = authenticated_userid(request)

        profile_filters = []

        if userid is not None:
            profiles = self.Session.query(Profile).\
                filter(Profile.users.any(username=userid))
            for p in profiles.all():
                profile_filters.append(functions.intersects(Activity.point,
                                       p.geometry))
                if p.code == 'global':
                    profile_filters.append(Activity.point == None)

        if len(profile_filters) > 0:
            return or_(* profile_filters)

        return None

    def _get_bbox_filter(self, request):
        """
        Return the spatial filter provided by the bbox in the parameters
        """

        if request.params.get('bbox', None) is not None:
            # Create a geometry filter based on a bbox

            # Get the EPSG code from the input geometry
            epsg = functions.srid(Activity.point)
            try:
                epsg = int(request.params.get('epsg', 4326))
            except ValueError:
                pass

            bbox = request.params.get('bbox', None)
            if bbox is not None:
                try:
                    box = map(float, bbox.split(','))
                    geometry = Polygon((
                                       (box[0], box[1]),
                                       (box[0], box[3]),
                                       (box[2], box[3]),
                                       (box[2], box[1]),
                                       (box[0], box[1]))
                                       )

                    # Create the intersection geometry
                    wkb_geometry = WKBSpatialElement(buffer(geometry.wkb), epsg)

                    # Get the SRID used in the Activity class
                    activity_srid = functions.srid(Activity.point)

                    # Return a subquery
                    return functions.intersects(
                        Activity.point, functions.transform(
                            wkb_geometry, activity_srid))
                except ValueError:
                    pass

        return None

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
            if involvement_change is not None
            and 'implicit_involvement_update' in activity_dict
            and activity_dict['implicit_involvement_update'] is True else False)

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
            db_a = self.Session.query(Activity).\
                filter(Activity.activity_identifier == identifier).\
                filter(Activity.version == old_version).\
                first()
            if db_a is None:
                # If no Activity was found, create a new one
                create_new = True

        if create_new is True:
            # Create new Activity
            new_activity = self._create_activity(request, activity_dict,
                changeset, status=status)

            # Handle also the involvements
            self._handle_involvements(request, None, new_activity,
                involvement_change, changeset, implicit_inv_change)

            return new_activity
        
        else:
            # Update existing Activity
            updated_activity = self._update_activity(request, db_a, activity_dict,
                changeset)

            # Handle also the involvements
            self._handle_involvements(request, db_a, updated_activity,
                involvement_change, changeset, implicit_inv_change)

            return updated_activity

    def _create_activity(self, request, activity_dict, changeset, **kwargs):
        """
        Creates a new Activity and handles its involvements.
        Allowed keyword arguments:
        - 'status'
        """

        identifier = (activity_dict['id'] if 'id' in activity_dict and
            activity_dict['id'] is not None
            else uuid.uuid4())

        # The initial version is 1
        version = 1

        # Try to get the geometry
        if ('geometry' in activity_dict and activity_dict['geometry']
            is not None):
            geom = geojson.loads(json.dumps(activity_dict['geometry']),
                                 object_hook=geojson.GeoJSON.to_instance)

            # The geometry
            shape = asShape(geom)
            # Create a new activity and add representative point to the activity
            new_activity = Activity(activity_identifier=identifier,
                version=version, point=shape.representative_point().wkt)
        else:
            # If no geometry is submitted, create new activity without geometry
            new_activity = Activity(activity_identifier=identifier,
                version=version)

        # Status (default: 'pending')
        status = 'pending'
        if 'status' in kwargs:
            status = kwargs['status']
        new_activity.status = self.Session.query(Status).\
            filter(Status.name == status).\
            first()

        # Initialize Tag Groups
        new_activity.tag_groups = []

        # Append the Changeset
        new_activity.changeset = changeset

        # Add the Activity to the database
        self.Session.add(new_activity)

        # Populate the Tag Groups
        for i, taggroup in enumerate(activity_dict['taggroups']):

            db_tg = A_Tag_Group(i+1)
            new_activity.tag_groups.append(db_tg)

            # Main Tag: First reset it. Then try to get it (its key and value)
            # from the dict.
            # The Main Tag is not mandatory.
            main_tag = None
            main_tag_key = None
            main_tag_value = None
            try:
                main_tag = taggroup['main_tag']
                main_tag_key = main_tag['key']
                main_tag_value = main_tag['value']
            except KeyError:
                pass

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

                # Create the new tag
                a_tag = self._create_tag(request, db_tg.tags, key, value, A_Tag,
                    A_Key, A_Value)

                # Check if the current tag is the main tag of this tag group. If
                # yes, set the main_tag attribute to this tag
                try:
                    if (a_tag.key.key == main_tag_key
                        and a_tag.value.value == main_tag_value):
                        db_tg.main_tag = a_tag
                except AttributeError:
                    pass

        return new_activity

    def _update_activity(self, request, old_activity, activity_dict, changeset,
        **kwargs):
        """
        Update an Activity. The basic idea is to deep copy the previous version
        and decide for each tag if it is to be deleted or not. At the end, new
        tags and new taggroups are added.
        Allowed keyword arguments:
        - 'status'
        """

        # Query latest version of current Activity (used to increase version)
        latest_version = self.Session.query(Activity).\
            filter(Activity.activity_identifier == old_activity.identifier).\
            order_by(desc(Activity.version)).\
            first()

        # Geometry
        new_geom = old_activity.point
        if 'geometry' in activity_dict:
            geojson_obj = geojson.loads(json.dumps(activity_dict['geometry']),
                                        object_hook=geojson.GeoJSON.to_instance)
            geojson_shape = asShape(geojson_obj)

            new_geom = geojson_shape.representative_point().wkt

        # Create new Activity
        new_activity = Activity(activity_identifier=old_activity.identifier,
            version=(latest_version.version+1), point=new_geom)

        # Status (default: 'pending')
        status = 'pending'
        if 'status' in kwargs:
            status = kwargs['status']
        new_activity.status = self.Session.query(Status).\
            filter(Status.name == status).\
            first()

        # Initialize Tag Groups
        new_activity.tag_groups = []

        # Append the Changeset
        new_activity.changeset = changeset

        # Add it to the database
        self.Session.add(new_activity)

        # Loop the tag groups from the previous version and copy it to the new
        # version with its tags
        for db_taggroup in self.Session.query(A_Tag_Group).\
            filter(A_Tag_Group.fk_activity == old_activity.id):

            # Create a new tag group but don't add it yet to the new activity
            # version. Indicator (taggroupadded) is needed because the moment
            # when to add a taggroup to database is a very delicate thing in
            # SQLAlchemy.
            taggroupadded = False
            new_taggroup = A_Tag_Group(db_taggroup.tg_id)

            # And loop the tags
            for db_tag in db_taggroup.tags:

                # Before copying the tag, make sure that it is not to delete
                copy_tag = True
                if 'taggroups' in activity_dict:
                    for taggroup_dict in activity_dict['taggroups']:
                        if ('id' in taggroup_dict and
                            taggroup_dict['id'] == db_taggroup.id):
                            # Check which tags we have to edit
                            for tag_dict in taggroup_dict['tags']:
                                if ('id' in tag_dict and
                                    tag_dict['id'] == db_tag.id):
                                    # Yes, it is THIS tag
                                    if tag_dict['op'] == 'delete':
                                        copy_tag = False

                # Create and append the new tag only if requested
                if copy_tag:
                    # Get the key and value SQLAlchemy object
                    k = self.Session.query(A_Key).get(db_tag.fk_key)
                    v = self.Session.query(A_Value).get(db_tag.fk_value)
                    new_tag = A_Tag()
                    new_taggroup.tags.append(new_tag)
                    new_tag.key = k
                    new_tag.value = v

                    # Set the main tag
                    if db_taggroup.main_tag == db_tag:
                        new_taggroup.main_tag = new_tag

                    if taggroupadded is False:
                        # It is necessary to add taggroup to database
                        # immediately, otherwise SQLAlchemy tries to do this the
                        # next time a tag is created and throws an error because
                        # of assumingly null values
                        new_activity.tag_groups.append(new_taggroup)
                        taggroupadded = True

            # Next step is to add new tags to this tag group without existing ids
            if 'taggroups' in activity_dict:
                for taggroup_dict in activity_dict['taggroups']:
                    if ('id' in taggroup_dict and
                        taggroup_dict['id'] == db_taggroup.id):
                        for tag_dict in taggroup_dict['tags']:
                            if 'id' not in tag_dict and tag_dict['op'] == 'add':
                                new_tag = self._create_tag(
                                    request, new_taggroup.tags, tag_dict['key'],
                                    tag_dict['value'], A_Tag, A_Key, A_Value)
                                # Set the main tag
                                if 'main_tag' in taggroup_dict:
                                    if (taggroup_dict['main_tag']['key'] ==
                                        new_tag.key.key and
                                        taggroup_dict['main_tag']['value'] ==
                                        new_tag.value.value):
                                        new_taggroup.main_tag = new_tag

            # If taggroups were not added to database yet, then do it now. But
            # only if add new tag groups to the new version if they have any
            # tags in them (which is not the case if they were deleted).
            if len(new_taggroup.tags) > 0 and taggroupadded is False:
                new_activity.tag_groups.append(new_taggroup)

        # Finally new tag groups (without id) needs to be added
        # (and loop all again)
        if 'taggroups' in activity_dict:
            for taggroup_dict in activity_dict['taggroups']:
                if (('id' not in taggroup_dict or ('id' in taggroup_dict and
                    taggroup_dict['id'] is None))
                    and taggroup_dict['op'] == 'add'):
                    # Find next empty tg_id
                    tg_id_q = self.Session.query(func.max(A_Tag_Group.tg_id)).\
                        join(Activity).\
                        filter(Activity.activity_identifier
                            == new_activity.activity_identifier).\
                        first()
                    new_taggroup = A_Tag_Group(tg_id_q[0] + 1)
                    new_activity.tag_groups.append(new_taggroup)
                    for tag_dict in taggroup_dict['tags']:
                        new_tag = self._create_tag(
                            request, new_taggroup.tags, tag_dict['key'],
                            tag_dict['value'], A_Tag, A_Key, A_Value)
                        # Set the main tag
                        if 'main_tag' in taggroup_dict:
                            if (taggroup_dict['main_tag']['key'] ==
                                new_tag.key.key and
                                taggroup_dict['main_tag']['value'] ==
                                new_tag.value.value):
                                new_taggroup.main_tag = new_tag

        return new_activity

    def _handle_involvements(self, request, old_version, new_version,
        inv_change, changeset, implicit=False):
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

        # It is important to keep track of all the Stakeholders where
        # involvements were deleted because they need to be pushed to a new
        # version as well
        swdi_id = [] # = Stakeholders with deleted involvements
        swdi_version = []
        swdi_role = []
        # Copy old involvements if existing
        if old_version is not None:
            for oi in old_version.involvements:
                # Check if involvement is to be removed (op == delete), in which
                # case do not copy it
                remove = False
                if inv_change is not None:
                    for i in inv_change:
                        if ('id' in i and str(i['id']) ==
                            str(oi.stakeholder.stakeholder_identifier) and
                            'op' in i and i['op'] == 'delete' and 'role' in i
                            and i['role'] == oi.stakeholder_role.id):
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
                if remove is not True and oi.stakeholder.status.id < 3:
                    sh_role = oi.stakeholder_role
                    sh = oi.stakeholder
                    # Copy involvement
                    inv = Involvement()
                    inv.stakeholder = sh
                    inv.activity = new_version
                    inv.stakeholder_role = sh_role
                    self.Session.add(inv)
        # Add new involvements
        if inv_change is not None:
            for i in inv_change:
                if ('op' in i and i['op'] == 'add' and
                    'id' in i and 'role' in i and 'version' in i):
                    # Query database to find role and previous version of
                    # Stakeholder
                    role_db = self.Session.query(Stakeholder_Role).\
                        get(i['role'])
                    old_sh_db = self.Session.query(Stakeholder).\
                        filter(Stakeholder.stakeholder_identifier == i['id']).\
                        filter(Stakeholder.version == i['version']).\
                        first()
                    if old_sh_db is not None:
                        # If the same Stakeholder also has some involvements
                        # deleted, remove it from the list (do not push
                        # Stakeholder twice)
                        try:
                            x = swdi_id.index(
                                str(old_sh_db.stakeholder_identifier))
                            swdi_id.pop(x)
                            swdi_version.pop(x)
                            swdi_role.pop(x)
                        except ValueError:
                            pass
                        # Push Stakeholder to new version
                        sp = StakeholderProtocol3(self.Session)
                        # Simulate a dict
                        sh_dict = {
                            'id': old_sh_db.stakeholder_identifier,
                            'version': old_sh_db.version
                        }
                        new_sh = sp._handle_stakeholder(request, sh_dict,
                            changeset)
                        # Create new inolvement
                        inv = Involvement()
                        inv.stakeholder = new_sh
                        inv.activity = new_version
                        inv.stakeholder_role = role_db
                        self.Session.add(inv)
        # Also push Stakeholders where involvements were deleted to new version
        if implicit is not True:
            for i, a in enumerate(swdi_id):
                # Query database
                old_sh_db = self.Session.query(Stakeholder).\
                    filter(Stakeholder.stakeholder_identifier == a).\
                    filter(Stakeholder.version == swdi_version[i]).\
                    first()
                # Push Stakeholder to new version
                sp = StakeholderProtocol3(self.Session)
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
                new_sh = sp._handle_stakeholder(request, sh_dict, changeset)