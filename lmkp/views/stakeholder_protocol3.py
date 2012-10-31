import logging

from lmkp.models.database_objects import *
from lmkp.views.protocol import *
from lmkp.views.translation import statusMap
from lmkp.views.translation import get_translated_status

from pyramid.i18n import get_localizer
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.expression import asc
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql.expression import or_
from sqlalchemy.sql.expression import not_
from sqlalchemy.sql.expression import select

class StakeholderProtocol3(Protocol):

    def __init__(self, Session):
        self.Session = Session

    def read_one_active(self, request, uid):

        relevant_stakeholders = self._get_relevant_stakeholders_one_active(uid)

        # Determine if and how detailed Involvements are to be displayed.
        # Default is: 'full'
        inv_details = request.params.get('involvements', 'full')

        query, count = self._query_many(request, relevant_stakeholders,
            involvements=inv_details!='none')

        stakeholders = self._query_to_stakeholders(request, query,
            involvements=inv_details, public_query=True)

        return {
            'total': count,
            'data': [sh.to_table(request) for sh in stakeholders]
        }

    def read_one(self, request, uid, public=True):
        """
        ''public'': Boolean
        """

        relevant_stakeholders = self._get_relevant_stakeholders_one(request,
            uid, public_query = public)

        # Determine if and how detailed Involvements are to be displayed.
        # Default is: 'full'
        inv_details = request.params.get('involvements', 'full')

        # Get limit and offset from request.
        # Defaults: limit = None / offset = 0
        limit = self._get_limit(request)
        offset = self._get_offset(request)

        query, count = self._query_many(request, relevant_stakeholders,
            limit=limit, offset=offset, involvements=inv_details!='none')

        stakeholders = self._query_to_stakeholders(request, query,
            involvements=inv_details, public_query = public)

        return {
            'total': count,
            'data': [sh.to_table(request) for sh in stakeholders]
        }

    def read_many(self, request, public=True):

        relevant_stakeholders = self._get_relevant_stakeholders_many(
            request, public_query=public)

        # Determine if and how detailed Involvements are to be displayed.
        # Default is: 'full'
        inv_details = request.params.get('involvements', 'full')

        # Get limit and offset from request.
        # Defaults: limit = None / offset = 0
        limit = self._get_limit(request)
        offset = self._get_offset(request)

        query, count = self._query_many(
            request, relevant_stakeholders, limit=limit, offset=offset,
            involvements=inv_details!='none')

        stakeholders = self._query_to_stakeholders(
            request, query, involvements=inv_details, public_query=public)

        return {
            'total': count,
            'data': [sh.to_table(request) for sh in stakeholders]
        }

    def read_many_by_activity(self, request, uid, public=True):

        relevant_stakeholders = self._get_relevant_stakeholders_by_activity(
            request, uid, public_query=public)

        # Determine if and how detailed Involvements are to be displayed.
        # Default is: 'full'
        inv_details = request.params.get('involvements', 'full')

        # Get limit and offset from request.
        # Defaults: limit = None / offset = 0
        limit = self._get_limit(request)
        offset = self._get_offset(request)

        query, count = self._query_many(
            request, relevant_stakeholders, limit=limit, offset=offset,
            involvements=inv_details!='none')

        stakeholders = self._query_to_stakeholders(
            request, query, involvements=inv_details, public_query=public)

        return {
            'total': count,
            'data': [sh.to_table(request) for sh in stakeholders]
        }

    def _get_relevant_stakeholders_one_active(self, uid):

        # Create relevant Stakeholders
        relevant_stakeholders = self.Session.query(
                Stakeholder.id.label('order_id'),
                func.char_length('').label('order_value'),
                Stakeholder.fk_status,
                Stakeholder.stakeholder_identifier
            ).\
            outerjoin(SH_Tag_Group).\
            filter(Stakeholder.stakeholder_identifier == uid).\
            filter(Stakeholder.fk_status == 2).\
            group_by(Stakeholder.id, Stakeholder.fk_status,
                Stakeholder.stakeholder_identifier, func.char_length(''))

        return relevant_stakeholders


    def _get_relevant_stakeholders_one(self, request, uid, public_query=False):
        """
        """

        logged_in, is_moderator = self._get_user_status(
            effective_principals(request))

        # Prepare dummy order query
        order_query = self.Session.query(
                Stakeholder.id,
                func.char_length('').label('value') # Dummy value
            ).\
            subquery()

        # Prepare status filter
        status_filter = self.Session.query(
                Status.id
            ).\
            filter(or_(* self._get_status_detail(request, public_query)))

        # Create relevant Stakeholders
        relevant_stakeholders = self.Session.query(
            Stakeholder.id.label('order_id'),
            order_query.c.value.label('order_value'),
            Stakeholder.fk_status,
            Stakeholder.stakeholder_identifier,
            Stakeholder.version
        )

        # Filter by UID
        relevant_stakeholders = relevant_stakeholders.\
            filter(Stakeholder.stakeholder_identifier == uid)

        # Status filter
        relevant_stakeholders = relevant_stakeholders.\
            filter(Stakeholder.fk_status.in_(status_filter))

        relevant_stakeholders = relevant_stakeholders.\
            outerjoin(SH_Tag_Group).\
            outerjoin(order_query, order_query.c.id == Stakeholder.id)

        # If logged in and it is not a public query, add pending versions by
        # current user to selection. This is not necessary for moderators
        # because they already see all pending versions
        if logged_in and public_query is False and not is_moderator:

            request_user_id = (request.user.id if request.user is not None
                else None)

            pending_stakeholders = self.Session.query(
                Stakeholder.id.label('order_id'),
                order_query.c.value.label('order_value'),
                Stakeholder.fk_status,
                Stakeholder.stakeholder_identifier,
                Stakeholder.version
            )

            pending_stakeholders = pending_stakeholders.\
                join(SH_Changeset).\
                filter(Stakeholder.stakeholder_identifier == uid).\
                filter(Stakeholder.fk_status == 1).\
                filter(SH_Changeset.fk_user == request_user_id)

            pending_stakeholders = pending_stakeholders.\
                outerjoin(SH_Tag_Group).\
                outerjoin(order_query, order_query.c.id == Stakeholder.id)

            relevant_stakeholders = pending_stakeholders.\
                union(relevant_stakeholders)

        # Join Stakeholders with Tag Groups and order_query, then group it
        relevant_stakeholders = relevant_stakeholders.\
            group_by(Stakeholder.id, Stakeholder.fk_status,
                Stakeholder.stakeholder_identifier, order_query.c.value,
                Stakeholder.version)

        # Order the Activity, default: by version
        relevant_stakeholders = relevant_stakeholders.\
            order_by(desc(Stakeholder.version))

        return relevant_stakeholders

    def _get_relevant_stakeholders_dict(self, request, dicts):
        """
        ''dicts'': Dicts containing the identifier and the version of the
          Stakeholders to query
        """

        # Prepare dicts
        dict_filter = []
        for d in dicts:
            dict_filter.append(and_(
                Stakeholder.stakeholder_identifier == d['identifier'],
                Stakeholder.version == d['version']
            ))

        # Prepare order: Get the order from request
        order_query, order_numbers = self._get_order(
            request, Stakeholder, SH_Tag_Group, SH_Tag, SH_Key, SH_Value,
            SH_Changeset
        )

        # Create relevant Stakeholders
        relevant_stakeholders = self.Session.query(
            Stakeholder.id.label('order_id'),
            order_query.c.value.label('order_value'),
            Stakeholder.fk_status,
            Stakeholder.stakeholder_identifier
        )

        # Dict filter
        relevant_stakeholders = relevant_stakeholders.filter(or_(*dict_filter))

        # Join Stakeholders with Tag Groups and order_query, then group it
        relevant_stakeholders = relevant_stakeholders.\
            outerjoin(SH_Tag_Group).\
            outerjoin(order_query, order_query.c.id == Stakeholder.id).\
            group_by(Stakeholder.id, order_query.c.value, Stakeholder.fk_status,
            Stakeholder.stakeholder_identifier)

        # Do the ordering
        if order_numbers is not None:
            if self._get_order_direction(request) == 'DESC':
                # Descending
                if order_numbers is True:
                    # Order by numbers: Cast values to float
                    relevant_stakeholders = relevant_stakeholders.order_by(
                        desc(cast(order_query.c.value, Float)))
                else:
                    # Order alphabetically
                    relevant_stakeholders = relevant_stakeholders.order_by(
                        desc(order_query.c.value))
            else:
                # Ascending
                if order_numbers is True:
                    # Order by numbers: Cast values to float
                    relevant_stakeholders = relevant_stakeholders.order_by(
                        asc(cast(order_query.c.value, Float)))
                else:
                    # Order alphabetically
                    relevant_stakeholders = relevant_stakeholders.order_by(
                        asc(order_query.c.value))

        return relevant_stakeholders

    def _get_relevant_stakeholders_many(self, request, filter=None,
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

        # Prepare filter based on Stakeholder attributes
        filter_subqueries = None
        if sh_filter_length == 0:
            # If no filter is provided: pass
            pass
        elif self._get_logical_operator(request) == 'or':
            # OR
            all_subqueries = []
            for x in sh_tag_filter:
                # Collect the Stakeholder IDs for each filter
                taggroups_sq = x.subquery()
                single_subquery = self.Session.query(
                        Stakeholder.id.label('sh_filter_id')
                    ).\
                    join(SH_Tag_Group).\
                    join(taggroups_sq,
                        taggroups_sq.c.sh_filter_tg_id == SH_Tag_Group.id)
                all_subqueries.append(single_subquery)
            # Put all found Stakeholder IDs together (UNION)
            filter_subqueries = all_subqueries[0].\
                union(* all_subqueries[1:]).\
                subquery()
        else:
            # AND
            filter_subqueries = self.Session.query(
                Stakeholder.id.label('sh_filter_id')
            )
            for x in sh_tag_filter:
                # Collect the Stakeholder IDs for each filter
                taggroups_sq = x.subquery()
                single_subquery = self.Session.query(
                        Stakeholder.id.label('sh_filter_id')
                    ).\
                    join(SH_Tag_Group).\
                    join(taggroups_sq,
                        taggroups_sq.c.sh_filter_tg_id == SH_Tag_Group.id).\
                    subquery()
                # Join each found Stakeholder ID with previously found IDs
                filter_subqueries = filter_subqueries.\
                    join(single_subquery,
                        single_subquery.c.sh_filter_id == Stakeholder.id)
            filter_subqueries = filter_subqueries.subquery()

        # Prepare order: Get the order from request
        order_query, order_numbers = self._get_order(
            request, Stakeholder, SH_Tag_Group, SH_Tag, SH_Key, SH_Value,
            SH_Changeset
        )

        # Create relevant Stakeholders
        relevant_stakeholders = self.Session.query(
            Stakeholder.id.label('order_id'),
            order_query.c.value.label('order_value'),
            Stakeholder.fk_status,
            Stakeholder.stakeholder_identifier
        )

        # Join Stakeholders with TagGroups
        if filter_subqueries is not None:
            # If a filter was provided, join with filtered subqueries
            relevant_stakeholders = relevant_stakeholders.\
                join(filter_subqueries,
                    filter_subqueries.c.sh_filter_id == Stakeholder.id)
        else:
            # If no filter was provided, simply join with SH_Tag_Group (outer
            # join to also capture empty Items)
            relevant_stakeholders = relevant_stakeholders.\
                outerjoin(SH_Tag_Group)

        # Join Stakeholders with order and group
        relevant_stakeholders = relevant_stakeholders.\
            outerjoin(order_query, order_query.c.id == Stakeholder.id)

        # Filter by timestamp
        # @TODO: do it!
        timestamp_filter = None

        # Apply status filter (only if timestamp filter is not set)
        if status_filter is not None and timestamp_filter is None:
            relevant_stakeholders = relevant_stakeholders.\
                filter(Stakeholder.fk_status.in_(status_filter))

        # If logged in and it is not a public query, add pending versions by
        # current user to selection. If moderator, add all pending versions.
        if logged_in and public_query is False:

            # It is necessary to first find out, if there are Stakeholders
            # pending and if yes, which is the latest version
            latest_pending_stakeholders = self.Session.query(
                    Stakeholder.stakeholder_identifier,
                    func.max(Stakeholder.version).label('max_version')
                ).\
                join(SH_Changeset).\
                filter(Stakeholder.fk_status == 1)

            if not is_moderator:
                # If current user is not a moderator, only show pending versions
                # done by himself
                latest_pending_stakeholders = latest_pending_stakeholders.\
                    filter(SH_Changeset.fk_user == request.user.id)

            latest_pending_stakeholders = latest_pending_stakeholders.\
                group_by(Stakeholder.stakeholder_identifier).\
                subquery()

            # Collect other information about pending Stakeholders (order, ...)
            pending_stakeholders = self.Session.query(
                    Stakeholder.id.label('order_id'),
                    order_query.c.value.label('order_value'),
                    Stakeholder.fk_status,
                    Stakeholder.stakeholder_identifier
                ).\
                join(latest_pending_stakeholders, and_(
                    latest_pending_stakeholders.c.max_version
                        == Stakeholder.version,
                    latest_pending_stakeholders.c.stakeholder_identifier
                        == Stakeholder.stakeholder_identifier
                ))

            # Join pending Stakeholders with TagGroups and filters to find out
            # if they are to be displayed at all
            if filter_subqueries is not None:
                # If a filter was provided, join with filtered subqueries
                pending_stakeholders = pending_stakeholders.\
                    join(filter_subqueries,
                        filter_subqueries.c.sh_filter_id == Stakeholder.id)
            else:
                # If no filter was provided, simply join with SH_Tag_Group
                # (outer join to also capture empty Items)
                pending_stakeholders = pending_stakeholders.\
                    outerjoin(SH_Tag_Group)

            # Join pending Stakeholders with order and group
            pending_stakeholders = pending_stakeholders.\
                outerjoin(order_query, order_query.c.id == Stakeholder.id).\
                group_by(Stakeholder.stakeholder_identifier, Stakeholder.id,
                    order_query.c.value)

            # Filter out the active Stakeholders if they have a pending version.
            # Then union with pending Stakeholders.
            relevant_stakeholders = relevant_stakeholders.filter(
                not_(Stakeholder.stakeholder_identifier.in_(
                    select([pending_stakeholders.subquery().\
                    c.stakeholder_identifier])
                ))
            )
            relevant_stakeholders = pending_stakeholders.union(
                relevant_stakeholders)

        relevant_stakeholders = relevant_stakeholders.\
            group_by(Stakeholder.id, order_query.c.value, Stakeholder.fk_status,
            Stakeholder.stakeholder_identifier)

        # Filter based on Activity attributes
        if a_filter_length > 0:
            # Prepare a dict to simulate filter for Activities
            a_filter_dict = {
                'a_tag_filter': a_tag_filter,
                'a_filter_length': a_filter_length,
                'status_filter': status_filter
            }
            # Use ActivityProtocol to query id's of Activities
            from lmkp.views.activity_protocol3 import ActivityProtocol3
            ap = ActivityProtocol3(self.Session)
            rel_a = ap._get_relevant_activities_many(
                request, filter=a_filter_dict)
            a_query = ap._query_only_id(rel_a)
            #a_query, c = ap._query(request, filter=a_filter_dict)
            a_subquery = a_query.subquery()
            if self._get_logical_operator(request) == 'or':
                # OR: use 'union' to add id's to relevant_stakeholders
                relevant_stakeholders = relevant_stakeholders.\
                    union(self.Session.query(
                            Stakeholder.id.label('order_id'),
                            func.char_length('').label('order_value'), # dummy
                            Stakeholder.fk_status,
                            Stakeholder.stakeholder_identifier
                        ).\
                        join(Involvement).\
                        join(a_subquery, a_subquery.c.id
                            == Involvement.fk_activity).\
                        group_by(Stakeholder.id)
                    )
            else:
                # AND: filter id's of relevant_stakeholders
                relevant_stakeholders = relevant_stakeholders.\
                    join(Involvement).\
                    join(a_subquery, a_subquery.c.id
                        == Involvement.fk_activity).\
                    group_by(Stakeholder.id)

        # Do the ordering
        if order_numbers is not None:
            if self._get_order_direction(request) == 'DESC':
                # Descending
                if order_numbers is True:
                    # Order by numbers: Cast values to float
                    relevant_stakeholders = relevant_stakeholders.order_by(
                        desc(cast(order_query.c.value, Float)))
                else:
                    # Order alphabetically
                    relevant_stakeholders = relevant_stakeholders.order_by(
                        desc(order_query.c.value))
            else:
                # Ascending
                if order_numbers is True:
                    # Order by numbers: Cast values to float
                    relevant_stakeholders = relevant_stakeholders.order_by(
                        asc(cast(order_query.c.value, Float)))
                else:
                    # Order alphabetically
                    relevant_stakeholders = relevant_stakeholders.order_by(
                        asc(order_query.c.value))

        return relevant_stakeholders

    def _get_relevant_stakeholders_by_activity(self, request, uid,
        public_query=False):

        logged_in, is_moderator = self._get_user_status(
            effective_principals(request))

        # Use ActivityProtocol to query the Activity versions corresponding to
        # given uid
        from lmkp.views.activity_protocol3 import ActivityProtocol3
        ap = ActivityProtocol3(self.Session)
        relevant_activities = ap._get_relevant_activities_one(request, uid=uid,
            public_query=public_query)

        # Always take the latest one.
        relevant_activities = relevant_activities.\
            limit(1).\
            subquery()

        # Prepare status filter
        status_filter = self.Session.query(
                    Status.id
                ).\
                filter(or_(* self._get_status(request)))

        # Prepare order: Get the order from request
        order_query, order_numbers = self._get_order(
            request, Stakeholder, SH_Tag_Group, SH_Tag, SH_Key, SH_Value,
            SH_Changeset
        )

        # Create relevant Stakeholders
        relevant_stakeholders = self.Session.query(
            Stakeholder.id.label('order_id'),
            order_query.c.value.label('order_value'),
            Stakeholder.fk_status,
            Stakeholder.stakeholder_identifier
        )
        
        # Filter trough Involvements to only take Stakeholders involved with 
        # relevant Activity
        relevant_stakeholders = relevant_stakeholders.\
            join(Involvement).\
            filter(Involvement.fk_activity.in_(
                select([relevant_activities.c.order_id])
            ))
        
        # Join Stakeholders with Tag Groups and order_query, then group it
        relevant_stakeholders = relevant_stakeholders.\
            outerjoin(SH_Tag_Group).\
            outerjoin(order_query, order_query.c.id == Stakeholder.id).\
            filter(Stakeholder.fk_status.in_(status_filter))
            
        # If logged in and it is not a public query, add pending versions by 
        # current user to selection. If moderator, add all pending versions.
        if logged_in and public_query is False:

            # It is necessary to first find out, if there are Stakeholders
            # pending and if yes, which is the latest version
            latest_pending_stakeholders = self.Session.query(
                    Stakeholder.stakeholder_identifier,
                    func.max(Stakeholder.version).label('max_version')
                ).\
                join(SH_Changeset).\
                filter(Stakeholder.fk_status == 1)

            if not is_moderator:
                # If current user is not a moderator, only show pending versions
                # done by himself
                latest_pending_stakeholders = latest_pending_stakeholders.\
                    filter(SH_Changeset.fk_user == request.user.id)

            latest_pending_stakeholders = latest_pending_stakeholders.\
                group_by(Stakeholder.stakeholder_identifier).\
                subquery()

            # Collect other information about pending Stakeholders (order, ...)
            pending_stakeholders = self.Session.query(
                    Stakeholder.id.label('order_id'),
                    order_query.c.value.label('order_value'),
                    Stakeholder.fk_status,
                    Stakeholder.stakeholder_identifier
                ).\
                join(latest_pending_stakeholders, and_(
                    latest_pending_stakeholders.c.max_version
                        == Stakeholder.version,
                    latest_pending_stakeholders.c.stakeholder_identifier
                        == Stakeholder.stakeholder_identifier
                ))

            # Filter trough Involvements to only take Stakeholders involved with
            # relevant Activities
            pending_stakeholders = pending_stakeholders.\
                join(Involvement).\
                filter(Involvement.fk_activity.in_(
                    select([relevant_activities.c.order_id])
                ))

            # Join Stakeholders with Tag Groups and order_query, then group it
            pending_stakeholders = pending_stakeholders.\
                outerjoin(SH_Tag_Group).\
                outerjoin(order_query, order_query.c.id == Stakeholder.id).\
                group_by(Stakeholder.stakeholder_identifier, Stakeholder.id,
                    order_query.c.value)

            # Filter out the active Stakeholders if they have a pending version.
            # Then union with pending Stakeholders.
            relevant_stakeholders = relevant_stakeholders.filter(
                not_(Stakeholder.stakeholder_identifier.in_(
                    select([pending_stakeholders.subquery().\
                    c.stakeholder_identifier])
                ))
            )
            relevant_stakeholders = pending_stakeholders.union(
                relevant_stakeholders)
            
        relevant_stakeholders = relevant_stakeholders.\
            group_by(Stakeholder.id, order_query.c.value, Stakeholder.fk_status,
            Stakeholder.stakeholder_identifier)

        # Do the ordering
        if order_numbers is not None:
            if self._get_order_direction(request) == 'DESC':
                # Descending
                if order_numbers is True:
                    # Order by numbers: Cast values to float
                    relevant_stakeholders = relevant_stakeholders.order_by(
                        desc(cast(order_query.c.value, Float)))
                else:
                    # Order alphabetically
                    relevant_stakeholders = relevant_stakeholders.order_by(
                        desc(order_query.c.value))
            else:
                # Ascending
                if order_numbers is True:
                    # Order by numbers: Cast values to float
                    relevant_stakeholders = relevant_stakeholders.order_by(
                        asc(cast(order_query.c.value, Float)))
                else:
                    # Order alphabetically
                    relevant_stakeholders = relevant_stakeholders.order_by(
                        asc(order_query.c.value))

        return relevant_stakeholders


    def _query_only_id(self, relevant_stakeholders):
        # Create query
        relevant_stakeholders = relevant_stakeholders.subquery()
        query = self.Session.query(
                Stakeholder.id.label('id')
            ).\
            join(relevant_stakeholders,
                relevant_stakeholders.c.order_id == Stakeholder.id)

        return query

    def _query_many(self, request, relevant_stakeholders, limit=None,
        offset=None, involvements=False, return_count=True):
        # Prepare query to translate keys and values
        localizer = get_localizer(request)
        lang = None if localizer.locale_name == 'en' \
            else self.Session.query(Language).\
                filter(Language.locale == localizer.locale_name).\
                first()
        key_translation, value_translation = self._get_translatedKV(lang,
            SH_Key, SH_Value)

        # Count
        if return_count:
            count = relevant_stakeholders.count()

        # Apply limit and offset
        if limit is not None:
            relevant_stakeholders = relevant_stakeholders.limit(limit)
        if offset is not None:
            relevant_stakeholders = relevant_stakeholders.offset(offset)

        # Create query
        relevant_stakeholders = relevant_stakeholders.subquery()
        query = self.Session.query(
                Stakeholder.id.label('id'),
                Stakeholder.stakeholder_identifier.label('identifier'),
                Stakeholder.version.label('version'),
                Status.id.label('status_id'),
                Status.name.label('status'),
                SH_Changeset.timestamp.label('timestamp'),
                SH_Tag_Group.id.label('taggroup'),
                SH_Tag_Group.fk_sh_tag.label('main_tag'),
                SH_Tag.id.label('tag'),
                SH_Key.key.label('key'),
                SH_Value.value.label('value'),
                key_translation.c.key_translated.label('key_translated'),
                value_translation.c.value_translated.label('value_translated'),
                relevant_stakeholders.c.order_value.label('order_value')
            ).\
            join(relevant_stakeholders,
                relevant_stakeholders.c.order_id == Stakeholder.id).\
            join(Status).\
            join(SH_Changeset).\
            outerjoin(SH_Tag_Group).\
            outerjoin(SH_Tag, SH_Tag_Group.id == SH_Tag.fk_sh_tag_group).\
            outerjoin(SH_Key).\
            outerjoin(SH_Value).\
            outerjoin(key_translation,
                key_translation.c.key_original_id == SH_Key.id).\
            outerjoin(value_translation,
                value_translation.c.value_original_id == SH_Value.id)

        if involvements:
            inv_status_filter = self.Session.query(
                    Status.id
                ).\
                filter(or_(* self._get_involvement_status(request)))
            inv_status = self.Session.query(
                    Activity.id.label('activity_id'),
                    Activity.activity_identifier.label('activity_identifier'),
                    Activity.fk_status.label('activity_status'),
                    Activity.version.label('activity_version')
                ).\
                filter(Activity.fk_status.in_(inv_status_filter)).\
                subquery()
            inv_query = self.Session.query(
                    Involvement.fk_stakeholder.label('stakeholder_id'),
                    Stakeholder_Role.id.label('role_id'),
                    Stakeholder_Role.name.label('role_name'),
                    A_Changeset.fk_user.label('activity_user_id'),
                    inv_status.c.activity_identifier.\
                        label('activity_identifier'),
                    inv_status.c.activity_status.label('activity_status'),
                    inv_status.c.activity_version.label('activity_version')
                ).\
                join(inv_status,
                    inv_status.c.activity_id == Involvement.fk_activity).\
                join(A_Changeset).\
                join(Stakeholder_Role).\
                subquery()

            query = query.\
                add_columns(
                    inv_query.c.activity_identifier.\
                        label('activity_identifier'),
                    inv_query.c.role_name.label('stakeholder_role'),
                    inv_query.c.role_id.label('stakeholder_role_id'),
                    inv_query.c.activity_status.label('activity_status'),
                    inv_query.c.activity_version.label('activity_version'),
                    inv_query.c.activity_user_id.label('activity_user_id')
                ).\
                outerjoin(inv_query,
                    inv_query.c.stakeholder_id == Stakeholder.id)

        if return_count:
            return query, count
        else:
            return query

    def _query_to_stakeholders(self, request, query,
        involvements='none', public_query=False):

        logged_in, is_moderator = self._get_user_status(
            effective_principals(request))

        # Put the Stakeholders together
        stakeholders = []
        for q in query.all():

            # Prepare values if needed
            identifier = str(q.identifier)
            taggroup_id = int(q.taggroup) if q.taggroup is not None else None
            key = q.key_translated if q.key_translated is not None else q.key
            value = (q.value_translated if q.value_translated is not None else
                q.value)

            # Use UID and version to find existing Feature or create a new one
            stakeholder = None
            for sh in stakeholders:
                if (sh.get_guid() == identifier and sh.get_version()
                    == q.version):
                    if not isinstance(q.order_value, int):
                        if sh.get_order_value() == q.order_value:
                            stakeholder = sh
                    else:
                        stakeholder = sh

            if stakeholder == None:
                stakeholder = Feature(
                    identifier, q.order_value, version=q.version,
                    timestamp=q.timestamp, status=q.status,
                    status_id=q.status_id
                )
                stakeholders.append(stakeholder)

            # Check if current Tag Group is already present in the Stakeholder
            taggroup = None
            if stakeholder.find_taggroup_by_id(taggroup_id) is not None:
                taggroup = stakeholder.find_taggroup_by_id(taggroup_id)
            else:
                taggroup = TagGroup(taggroup_id, q.main_tag)
                stakeholder.add_taggroup(taggroup)

            # Because of Involvements, the same Tags appears for each
            # Involvement, so add it only once to TagGroup
            if taggroup is not None and taggroup.get_tag_by_id(q.tag) is None:
                taggroup.add_tag(Tag(q.tag, key, value))

            # Involvements
            if involvements != 'none':
                try:
                    if q.activity_identifier is not None:

                        request_user_id = (request.user.id if request.user is 
                            not None else None)

                        # Flag indicating if Involvement to this Activity is not
                        # yet found ('none') or not to be added ('false')
                        inv = self._flag_add_involvement(
                            stakeholder,
                            q.status_id,
                            q.activity_status,
                            q.activity_identifier,
                            q.activity_version,
                            q.activity_user_id,
                            q.stakeholder_role,
                            request_user_id,
                            public_query,
                            logged_in,
                            is_moderator
                        )

                        if inv is None:
                            # Create new Involvement and add it to Stakeholder
                            # Default: only basic information about Involvement
                            stakeholder.add_involvement(
                                Inv(
                                    q.activity_identifier,
                                    None,
                                    q.stakeholder_role,
                                    q.stakeholder_role_id,
                                    q.activity_version,
                                    q.activity_status
                                )
                            )

                except ValueError:
                    pass

        if involvements == 'full':
            # If full involvements are to be shown, collect the identifiers and
            # versions of each Activity and prepare a dict. Query the details
            # (Tag Groups) of these Activities using the ActivityProtocol and
            # replace the existing Involvements. Query them all at once to
            # improve performance.

            inv_dicts = []
            for stakeholder in stakeholders:
                for i in stakeholder._involvements:
                    inv_dicts.append({
                        'identifier': i.get_guid(),
                        'version': i.get_version()
                    })

            # Use ActivityProtocol to query the details of the Activities
            from lmkp.views.activity_protocol3 import ActivityProtocol3
            ap = ActivityProtocol3(self.Session)
            relevant_activities = ap._get_relevant_activities_dict(
                request, inv_dicts)

            a_query = ap._query_many(request, relevant_activities,
                involvements=False, return_count=False)
            activities = ap._query_to_activities(request, a_query,
                involvements='none')

            # Loop through all existing Involvements
            for stakeholder in stakeholders:
                for index, i in enumerate(stakeholder._involvements):
                    # Try to find the current Activity in the detailed list
                    activity = None
                    for a in activities:
                        if (str(a.get_guid()) == str(i.get_guid())
                            and a.get_version() == i.get_version()):
                            activity = a

                    if activity is not None:
                        # If Activity was found, replace Involvement with full
                        # details
                        stakeholder._involvements[index] = Inv(
                            i.get_guid(),
                            activity,
                            i.get_role(),
                            i.get_role_id(),
                            i.get_version(),
                            i.get_status()
                        )

        return stakeholders