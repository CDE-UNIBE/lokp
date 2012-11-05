import logging

from lmkp.models.database_objects import *
from lmkp.views.protocol import *
from lmkp.views.translation import statusMap
from lmkp.views.translation import get_translated_status

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.i18n import get_localizer
from pyramid.security import authenticated_userid
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

    def create(self, request, data=None):
        """
        Create or update Stakeholders
        """

        diff = request.json_body if data is None else data

        user = self.Session.query(User).\
            filter(User.username == authenticated_userid(request)).\
            first()

        # Changeset
        changeset = Changeset()
        changeset.user = user

        # Check if the json body is a valid diff file
        if 'stakeholders' not in diff:
            raise HTTPBadRequest(detail="Not a valid format")

        # Get the current configuration file to validate key and value pairs
        self.configuration = self._read_configuration(request,
            'stakeholder.yml')

        # Return the IDs of the newly created Stakeholders
        ids = []
        for stakeholder in diff['stakeholders']:

            sh = self._handle_stakeholder(request, stakeholder, changeset)

            # Add the newly created identifier to the diff
            stakeholder[unicode('id')] = unicode(sh.stakeholder_identifier)

            ids.append(sh)

        # Save diff to changeset and handle UTF-8 of diff
        changeset.diff = str(self._convert_utf8(diff))

        return ids

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

        # Order the Stakeholder by version
        query = query.order_by(desc(Stakeholder.version))

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
                join(Changeset).\
                filter(Stakeholder.stakeholder_identifier == uid).\
                filter(Stakeholder.fk_status == 1).\
                filter(Changeset.fk_user == request_user_id)

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
            request, Stakeholder, SH_Tag_Group, SH_Tag, SH_Key, SH_Value
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
            request, Stakeholder, SH_Tag_Group, SH_Tag, SH_Key, SH_Value
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

            # It is necessary to first find out if there are Stakeholders
            # pending and if yes, which is the latest version
            latest_pending_stakeholders = self.Session.query(
                    Stakeholder.stakeholder_identifier,
                    func.max(Stakeholder.version).label('max_version')
                ).\
                join(Changeset).\
                filter(Stakeholder.fk_status == 1)

            if not is_moderator:
                # If current user is not a moderator, only show pending versions
                # done by himself
                latest_pending_stakeholders = latest_pending_stakeholders.\
                    filter(Changeset.fk_user == request.user.id)

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
            request, Stakeholder, SH_Tag_Group, SH_Tag, SH_Key, SH_Value
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
                join(Changeset).\
                filter(Stakeholder.fk_status == 1)

            if not is_moderator:
                # If current user is not a moderator, only show pending versions
                # done by himself
                latest_pending_stakeholders = latest_pending_stakeholders.\
                    filter(Changeset.fk_user == request.user.id)

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
                Changeset.timestamp.label('timestamp'),
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
            join(Changeset).\
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
                    Changeset.fk_user.label('activity_user_id'),
                    inv_status.c.activity_identifier.\
                        label('activity_identifier'),
                    inv_status.c.activity_status.label('activity_status'),
                    inv_status.c.activity_version.label('activity_version')
                ).\
                join(inv_status,
                    inv_status.c.activity_id == Involvement.fk_activity).\
                join(Changeset, Changeset.id == inv_status.c.activity_id).\
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

    def _handle_stakeholder(self, request, stakeholder_dict, changeset,
        status='pending'):
        """
        Handles a single Stakeholder and decides whether to create a new
        Stakeholder or update an existing one.
        """

        # Collect information about changing involvements
        involvement_change = (stakeholder_dict['activities']
            if 'activities' in stakeholder_dict
            else None)
        implicit_inv_change = (True
            if involvement_change is not None
            and 'implicit_involvement_update' in stakeholder_dict
            and stakeholder_dict['implicit_involvement_update'] is True
            else False)

        create_new = False

        # If there is no id for the Stakeholder in the diff, create a new
        # Stakeholder
        if 'id' not in stakeholder_dict:
            create_new = True
        else:
            # If there is an ID in the diff, try to find the Stakeholder based
            # on the identifier and version
            identifier = stakeholder_dict['id']
            old_version = (stakeholder_dict['version'] if 'version' in
                stakeholder_dict else None)
            db_sh = self.Session.query(Stakeholder).\
                filter(Stakeholder.stakeholder_identifier == identifier).\
                filter(Stakeholder.version == old_version).\
                first()
            if db_sh is None:
                # If no Stakeholder is found, create a new one
                create_new = True

        if create_new is True:
            # Create new Stakeholder
            new_stakeholder = self._create_stakeholder(request,
                stakeholder_dict, changeset, status=status)

            # Handle also the involvements
            self._handle_involvements(request, None, new_stakeholder,
                involvement_change, changeset, implicit_inv_change)

            return new_stakeholder

        else:
            # Update existing Stakeholder
            updated_stakeholder = self._update_stakeholder(request, db_sh, 
                stakeholder_dict, changeset)

            # Handle also the involvements
            self._handle_involvements(request, db_sh, updated_stakeholder,
                involvement_change, changeset, implicit_inv_change)

            return updated_stakeholder

    def _create_stakeholder(self, request, stakeholder_dict, changeset,
        **kwargs):
        """
        Creates a new Stakeholder. Allowed keyword arguments:
        'identifier'
        'status'
        """

        identifier = (stakeholder_dict['id'] if 'id' in stakeholder_dict and
            stakeholder_dict['id'] is not None
            else uuid.uuid4())

        # The initial version is 1
        version = 1

        # Create a new stakeholder
        new_stakeholder = Stakeholder(stakeholder_identifier=identifier,
            version=version)

        # Status (default: 'pending')
        status = 'pending'
        # Get the stakeholder status, default is pending
        if 'status' in kwargs:
            status = kwargs['status']
        new_stakeholder.status = self.Session.query(Status).\
            filter(Status.name == status).\
            first()

        # Initialize Tag Groups
        new_stakeholder.tag_groups = []

        # Append the Changeset
        new_stakeholder.changeset = changeset

        # Add the Stakeholder to the database
        self.Session.add(new_stakeholder)

        # Populate the Tag Groups
        for i, taggroup in enumerate(stakeholder_dict['taggroups']):

            db_tg = SH_Tag_Group(i+1)
            new_stakeholder.tag_groups.append(db_tg)

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

                sh_tag = self._create_tag(request, db_tg.tags, key, value,
                    SH_Tag, SH_Key, SH_Value)

                # Check if the current tag is the main tag of this tag group. If
                # yes, set the main_tag attribute to this tag
                try:
                    if (sh_tag.key.key == main_tag_key
                        and sh_tag.value.value == main_tag_value):
                        db_tg.main_tag = sh_tag
                except AttributeError:
                    pass

        return new_stakeholder

    def _update_stakeholder(self, request, old_stakeholder, stakeholder_dict,
        changeset, **kwargs):
        """
        Update a Stakeholder. The basic idea is to deep copy the previous
        version and decide for each tag if it is to be deleted or not. At the
        end, new tags and new taggroups are added.
        Allowed keyword arguments:
        - 'status'
        """

        # Query latest version of current Stakeholder (used to increase version)
        latest_version = self.Session.query(Stakeholder).\
            filter(Stakeholder.stakeholder_identifier
                == old_stakeholder.identifier).\
            order_by(desc(Stakeholder.version)).\
            first()

        # Create new Stakeholder
        new_stakeholder = Stakeholder(
            stakeholder_identifier=old_stakeholder.identifier,
            version=(latest_version.version+1))

        # Status (default: 'pending')
        status = 'pending'
        if 'status' in kwargs:
            status = kwargs['status']
        new_stakeholder.status = self.Session.query(Status).\
            filter(Status.name == status).\
            first()

        # Initialize Tag Groups
        new_stakeholder.tag_groups = []

        # Append the Changeset
        new_stakeholder.changeset = changeset

        # Add it to the database
        self.Session.add(new_stakeholder)

        # Loop the tag groups from the previous version and copy it to the new
        # version with its tags
        for db_taggroup in self.Session.query(SH_Tag_Group).\
            filter(SH_Tag_Group.fk_stakeholder == old_stakeholder.id):

            # Create a new tag group but don't add it yet to the new stakeholder
            # version. Indicator (taggroupadded) is needed because the moment
            # when to add a taggroup to database is a very delicate thing in
            # SQLAlchemy.
            taggroupadded = False
            new_taggroup = SH_Tag_Group(db_taggroup.tg_id)

            # And loop the tags
            for db_tag in db_taggroup.tags:

                # Before copying the tag, make sure that it is not to delete
                copy_tag = True
                if 'taggroups' in stakeholder_dict:
                    for taggroup_dict in stakeholder_dict['taggroups']:
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
                    k = self.Session.query(SH_Key).get(db_tag.fk_key)
                    v = self.Session.query(SH_Value).get(db_tag.fk_value)
                    new_tag = SH_Tag()
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
                        new_stakeholder.tag_groups.append(new_taggroup)
                        taggroupadded = True

            # Next step is to add new tags to this tag group without existing ids
            if 'taggroups' in stakeholder_dict:
                for taggroup_dict in stakeholder_dict['taggroups']:
                    if ('id' in taggroup_dict and
                        taggroup_dict['id'] == db_taggroup.id):
                        for tag_dict in taggroup_dict['tags']:
                            if 'id' not in tag_dict and tag_dict['op'] == 'add':
                                new_tag = self._create_tag(
                                    request, new_taggroup.tags, tag_dict['key'],
                                    tag_dict['value'], SH_Tag, SH_Key, SH_Value)
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
                new_stakeholder.tag_groups.append(new_taggroup)

        # Finally new tag groups (without id) needs to be added
        # (and loop all again)
        if 'taggroups' in stakeholder_dict:
            for taggroup_dict in stakeholder_dict['taggroups']:
                if (('id' not in taggroup_dict or ('id' in taggroup_dict and
                    taggroup_dict['id'] is None)) and
                    taggroup_dict['op'] == 'add'):
                    new_taggroup = SH_Tag_Group()
                    new_stakeholder.tag_groups.append(new_taggroup)
                    for tag_dict in taggroup_dict['tags']:
                        new_tag = self._create_tag(
                            request, new_taggroup.tags, tag_dict['key'],
                            tag_dict['value'], SH_Tag, SH_Key, SH_Value)
                        # Set the main tag
                        if 'main_tag' in taggroup_dict:
                            if (taggroup_dict['main_tag']['key'] ==
                                new_tag.key.key and
                                taggroup_dict['main_tag']['value'] ==
                                new_tag.value.value):
                                new_taggroup.main_tag = new_tag

        return new_stakeholder

    def _handle_involvements(self, request, old_version, new_version,
        inv_change, changeset, implicit=False):
        """
        Handle the involvements of a Stakeholder.
        - Stakeholder update: copy old involvements
        - Involvement added: copy old involvements, push Activity to new
            version, add new involvement
        - Involvement deleted: copy old involvements (except the one to be
            removed), push Activity to new version
        - Involvement modified (eg. its role): combination of deleting and
            adding involvements
        """
        from lmkp.views.activity_protocol3 import ActivityProtocol3
        # It is important to keep track of all the Activities where involvements
        # were deleted because they need to be pushed to a new version as well
        awdi_id = [] # = Activities with deleted involvements
        awdi_version = []
        awdi_role = []
        # Copy old involvements if existing
        if old_version is not None:
            for oi in old_version.involvements:
                # Check if involvement is to be removed (op == delete), in which
                # case do not copy it
                remove = False
                if inv_change is not None:
                    for i in inv_change:
                        if ('id' in i and str(i['id']) ==
                            str(oi.activity.activity_identifier) and
                            'op' in i and i['op'] == 'delete' and 'role' in i
                            and i['role'] == oi.stakeholder_role.id):
                            # Set flag to NOT copy this involvement
                            remove = True
                            # Add identifier and version of Activity to list
                            # with deleted involvements, add them only once
                            if i['id'] not in awdi_id:
                                awdi_id.append(i['id'])
                                awdi_version.append(i['version'])
                                awdi_role.append(i['role'])
                # Also: only copy involvements if status of Activity is
                # 'pending' or 'active'
                if remove is not True and oi.activity.status.id < 3:
                    sh_role = oi.stakeholder_role
                    a = oi.activity
                    # Copy involvement
                    inv = Involvement()
                    inv.stakeholder = new_version
                    inv.activity = a
                    inv.stakeholder_role = sh_role
                    self.Session.add(inv)
        # Add new involvements
        if inv_change is not None:
            for i in inv_change:
                if ('op' in i and i['op'] == 'add' and
                    'id' in i and 'role' in i and 'version' in i):
                    # Query database to find role and previous version of
                    # Activity
                    role_db = self.Session.query(Stakeholder_Role).\
                        get(i['role'])
                    old_a_db = self.Session.query(Activity).\
                        filter(Activity.activity_identifier == i['id']).\
                        filter(Activity.version == i['version']).\
                        first()
                    if old_a_db is not None:
                        # If the same Activity also has some involvements
                        # deleted, remove it from the list (do not push Activity
                        # twice)
                        try:
                            x = awdi_id.index(str(old_a_db.activity_identifier))
                            awdi_id.pop(x)
                            awdi_version.pop(x)
                            awdi_role.pop(x)
                        except ValueError:
                            pass
                        # Push Activity to new version
                        sp = ActivityProtocol3(self.Session)
                        # Simulate a dict
                        a_dict = {
                            'id': old_a_db.activity_identifier,
                            'version': old_a_db.version
                        }
                        new_a = sp._handle_activity(request, a_dict, changeset)
                        # Create new inolvement
                        inv = Involvement()
                        inv.stakeholder = new_version
                        inv.activity = new_a
                        inv.stakeholder_role = role_db
                        self.Session.add(inv)
        # Also push Activity where involvements were deleted to new version
        if implicit is not True:
            for i, a in enumerate(awdi_id):
                # Query database
                old_a_db = self.Session.query(Activity).\
                    filter(Activity.activity_identifier == a).\
                    filter(Activity.version == awdi_version[i]).\
                    first()
                # Push Activity to new version
                sp = ActivityProtocol3(self.Session)
                # Simulate a dict
                a_dict = {
                    'id': old_a_db.activity_identifier,
                    'version': old_a_db.version,
                    'stakeholders': [{
                        'op': 'delete',
                        'id': old_version.stakeholder_identifier,
                        'version': awdi_version[i],
                        'role': awdi_role[i]
                    }],
                    'implicit_involvement_update': True
                }
                new_a = sp._handle_activity(request, a_dict, changeset)