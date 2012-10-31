import logging

from lmkp.models.database_objects import *
from lmkp.views.protocol import *
from lmkp.views.stakeholder_protocol3 import StakeholderProtocol3
from lmkp.views.translation import statusMap
from lmkp.views.translation import get_translated_status

from geoalchemy import WKBSpatialElement
from geoalchemy.functions import functions
from pyramid.i18n import get_localizer
from pyramid.security import authenticated_userid
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
                join(A_Changeset).\
                filter(Activity.activity_identifier == uid).\
                filter(Activity.fk_status == 1).\
                filter(A_Changeset.fk_user == request_user_id)

            pending_activities = pending_activities.\
                outerjoin(A_Tag_Group).\
                outerjoin(order_query, order_query.c.id == Activity.id)

            relevant_activities = pending_activities.union(relevant_activities)

        # Join Activities with Tag Groups and order_query, then group it
        relevant_activities = relevant_activities.\
            group_by(Activity.id, Activity.fk_status,
                Activity.activity_identifier, order_query.c.value,
                Activity.version)

        # Order the Activity, default: by version
        relevant_activities = relevant_activities.\
            order_by(desc(Activity.version))

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
            request, Activity, A_Tag_Group, A_Tag, A_Key, A_Value, A_Changeset
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
            request, Activity, A_Tag_Group, A_Tag, A_Key, A_Value, A_Changeset
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

            # It is necessary to first find out, if there are Activities pending
            # and if yes, which is the latest version
            latest_pending_activities = self.Session.query(
                    Activity.activity_identifier,
                    func.max(Activity.version).label('max_version')
                ).\
                join(A_Changeset).\
                filter(Activity.fk_status == 1)

            if not is_moderator:
                # If current user is not a moderator, only show pending versions
                # done by himself
                latest_pending_activities = latest_pending_activities.\
                    filter(A_Changeset.fk_user == request.user.id)

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
            request, Activity, A_Tag_Group, A_Tag, A_Key, A_Value, A_Changeset
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
                join(A_Changeset).\
                filter(Activity.fk_status == 1)
            
            if not is_moderator:
                # If current user is not a moderator, only show pending versions
                # done by himself
                latest_pending_activities = latest_pending_activities.\
                    filter(A_Changeset.fk_user == request.user.id)
                
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
                A_Changeset.timestamp.label('timestamp'),
                A_Tag_Group.id.label('taggroup'),
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
            join(A_Changeset).\
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
                    SH_Changeset.fk_user.label('stakeholder_user_id'),
                    inv_status.c.stakeholder_identifier.\
                        label('stakeholder_identifier'),
                    inv_status.c.stakeholder_status.label('stakeholder_status'),
                    inv_status.c.stakeholder_version.\
                        label('stakeholder_version')
                ).\
                join(inv_status,
                    inv_status.c.stakeholder_id == Involvement.fk_stakeholder).\
                join(SH_Changeset).\
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
                taggroup = TagGroup(taggroup_id, q.main_tag)
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

    def _get_spatial_moderator_filter(self, request):
        """
        """
        userid = authenticated_userid(request)

        profile_filters = []

        if userid is not None:
            profiles = self.Session.query(Profile).\
                filter(Profile.users.any(username=userid))
            for p in profiles.all():
                print p
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

    