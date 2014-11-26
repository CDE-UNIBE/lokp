from sqlalchemy import func
from sqlalchemy.sql.expression import (
    and_,
    asc,
    desc,
    or_,
)

from lmkp.authentication import get_user_privileges
from lmkp.models.database_objects import (
    SH_Key,
    SH_Value,
    SH_Tag,
    SH_Tag_Group,
    Activity,
    Changeset,
    Institution,
    Involvement,
    Stakeholder,
    Stakeholder_Role,
    Status,
    User,
)
from lmkp.protocols.features import (
    ItemFeature,
    ItemTag,
    ItemTaggroup,
)
from lmkp.protocols.protocol import Protocol
from lmkp.views.protocol import Inv
from lmkp.views.views import (
    get_current_logical_filter_operator,
    get_current_order_direction,
    get_current_involvement_details,
    get_current_limit,
    get_current_offset,
)


class StakeholderProtocol(Protocol):
    """
    TODO
    """

    def read_many(
            self, public_query=True, limit=None, offset=None, translate=True):
        """
        TODO
        """

        relevant_query = self.get_relevant_query_many(
            public_query=public_query)

        involvement_details = get_current_involvement_details(self.request)
        show_involvements = involvement_details != 'none'

        if limit is None:
            limit = get_current_limit(self.request)
        if offset is None:
            offset = get_current_offset(self.request)

        query, count = self.query_many(
            relevant_query, limit=limit, offset=offset,
            with_involvements=show_involvements)

        features = self.query_to_features(
            query, involvements=involvement_details, public_query=public_query,
            translate=translate)

        return {
            'total': count,
            'data': [f.to_json(self.request) for f in features]
        }

    def get_relevant_query_from_list(self, stakeholder_list):
        """
        TODO
        """
        # Prepare filters with the dict
        dict_filter = []
        for sh in stakeholder_list:
            dict_filter.append(and_(
                Stakeholder.stakeholder_identifier == sh.get('identifier'),
                Stakeholder.version == sh.get('version')))

        # Prepare order: Get the order from request
        order_query = self.get_order('sh')

        relevant_query = self.Session.query(
            Stakeholder.id.label('order_id'),
            order_query.c.value.label('order_value'),
            Stakeholder.fk_status,
            Stakeholder.stakeholder_identifier
        ).filter(or_(* dict_filter))

        # Join Stakeholders with Taggroups and order_query, then group it
        relevant_query = relevant_query.\
            outerjoin(SH_Tag_Group).\
            outerjoin(order_query, order_query.c.id == Stakeholder.id).\
            group_by(
                Stakeholder.id, order_query.c.value, Stakeholder.fk_status,
                Stakeholder.stakeholder_identifier)

        # Do the ordering
        if get_current_order_direction(self.request) == 'desc':
            relevant_query = relevant_query.order_by(
                desc(order_query.c.value))
        else:
            relevant_query = relevant_query.order_by(
                asc(order_query.c.value))

        return relevant_query

    def get_relevant_query_many(self, filter=None, public_query=False):
        """
        TODO
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
        order_query = self.get_order('sh')

        relevant_query = self.Session.query(
            Stakeholder.id.label('order_id'),
            order_query.c.value.label('order_value'),
            Stakeholder.fk_status,
            Stakeholder.stakeholder_identifier
        )

        # Stakeholder attribute filters
        filter_subquery = None
        if len(sh_tag_filters) == 0:
            pass
        elif get_current_logical_filter_operator(self.request) == 'or':
            """
            Logical "or" filter: Use subqueries to collect the IDs of
            all Items matching each filter. Perform a SQL UNION based on
            the first subquery to unite all other subqueries and put all
            Item IDs together.
            """
            subqueries = []
            for tag_filter in sh_tag_filters:
                tag_filter_subquery = tag_filter.subquery()
                subquery = self.Session.query(
                    Stakeholder.id.label('sh_filter_id')
                ).\
                    join(SH_Tag_Group).\
                    join(tag_filter_subquery,
                         tag_filter_subquery.c.sh_filter_tg_id
                         == SH_Tag_Group.id)
                subqueries.append(subquery)
            filter_subquery = subqueries[0].union(* subqueries[1:]).subquery()
        else:
            """
            Logical "and" filter: Create a subquery by joining every
            filter subquery.
            """
            filter_subquery = self.Session.query(
                Stakeholder.id.label('sh_filter_id')
            )
            for tag_filter in sh_tag_filters:
                tag_filter_subquery = tag_filter.subquery()
                subquery = self.Session.query(
                    Stakeholder.id.label('sh_filter_id')
                ).\
                    join(SH_Tag_Group).\
                    join(tag_filter_subquery,
                         tag_filter_subquery.c.sh_filter_tg_id
                         == SH_Tag_Group.id).\
                    subquery()
                filter_subquery = filter_subquery.\
                    join(subquery, subquery.c.sh_filter_id == Stakeholder.id)
            filter_subquery = filter_subquery.subquery()

        # Join Stakeholders with TagGroups
        if filter_subquery is not None:
            # If a filter was provided, join with filtered subqueries
            relevant_query = relevant_query.\
                join(filter_subquery,
                     filter_subquery.c.sh_filter_id == Stakeholder.id)
        else:
            # If no filter was provided, simply join with SH_Tag_Group (outer
            # join to also capture empty Items)
            relevant_query = relevant_query.\
                outerjoin(SH_Tag_Group)

        # Join Stakeholders with order and group
        relevant_query = relevant_query.\
            outerjoin(order_query, order_query.c.id == Stakeholder.id)

        # Decide which version is based on status filter and user
        # privileges.
        relevant_query = self.apply_visible_version_filter(
            'sh', relevant_query, public_query=public_query)

        relevant_query = relevant_query.\
            group_by(
                Stakeholder.id, order_query.c.value, Stakeholder.fk_status,
                Stakeholder.stakeholder_identifier)

        # Filter based on Activity attributes
        if len(a_tag_filters) > 0:
            TODO
            # Prepare a dict to simulate filter for Activities
            a_filter_dict = {
                'a_tag_filter': a_tag_filters,
                'a_filter_length': len(a_tag_filters),
                'status_filter': status_filter
            }
            # Use ActivityProtocol to query id's of Activities
            from lmkp.views.activity_protocol3 import ActivityProtocol3
            ap = ActivityProtocol3(self.Session)
            rel_a = ap._get_relevant_activities_many(
                self.request, filter=a_filter_dict)
            a_query = ap._query_only_id(rel_a)
            #a_query, c = ap._query(request, filter=a_filter_dict)
            a_subquery = a_query.subquery()
            if self._get_logical_operator(self.request) == 'or':
                # OR: use 'union' to add id's to relevant_stakeholders
                relevant_query = relevant_query.\
                    union(self.Session.query(
                          Stakeholder.id.label('order_id'),
                          func.char_length('').label('order_value'),  # dummy
                          Stakeholder.fk_status,
                          Stakeholder.stakeholder_identifier
                          ).
                          join(Involvement).
                          join(a_subquery, a_subquery.c.id
                               == Involvement.fk_activity).
                          group_by(Stakeholder.id)
                          )
            else:
                # AND: filter id's of relevant_query
                relevant_query = relevant_query.\
                    join(Involvement).\
                    join(a_subquery, a_subquery.c.id
                         == Involvement.fk_activity).\
                    group_by(Stakeholder.id)

        # Do the ordering
        if get_current_order_direction(self.request) == 'desc':
            relevant_query = relevant_query.order_by(
                desc(order_query.c.value))
        else:
            relevant_query = relevant_query.order_by(
                asc(order_query.c.value))

        return relevant_query

    def query_many(
            self, relevant_query, limit=None, offset=None,
            with_involvements=False, return_count=True,
            with_metadata=False):
        """
        TODO
        """
        key_translation, value_translation = self.get_translation_queries('sh')

        # Count
        if return_count:
            count = relevant_query.count()

        # Apply limit and offset
        if limit is not None:
            relevant_query = relevant_query.limit(limit)
        if offset is not None:
            relevant_query = relevant_query.offset(offset)

        # Create query
        relevant_query = relevant_query.subquery()
        query = self.Session.query(
            Stakeholder.id.label('id'),
            Stakeholder.stakeholder_identifier.label('identifier'),
            Stakeholder.version.label('version'),
            Status.id.label('status_id'),
            Status.name.label('status'),
            Changeset.timestamp.label('timestamp'),
            SH_Tag_Group.id.label('taggroup'),
            SH_Tag_Group.tg_id.label('tg_id'),
            SH_Tag_Group.fk_sh_tag.label('main_tag'),
            SH_Tag.id.label('tag'),
            SH_Key.key.label('key'),
            SH_Value.value.label('value'),
            key_translation.c.key_translated.label('key_translated'),
            value_translation.c.value_translated.label('value_translated'),
            relevant_query.c.order_value.label('order_value')
        ).\
            join(relevant_query,
                 relevant_query.c.order_id == Stakeholder.id).\
            join(Status).\
            join(Changeset).\
            outerjoin(SH_Tag_Group).\
            outerjoin(SH_Tag, SH_Tag_Group.id == SH_Tag.fk_sh_tag_group).\
            outerjoin(SH_Key).\
            outerjoin(SH_Value, SH_Tag.fk_value == SH_Value.id).\
            outerjoin(key_translation,
                      key_translation.c.key_original_id == SH_Key.id).\
            outerjoin(value_translation,
                      value_translation.c.value_original_id == SH_Value.id)

        # Do the ordering again: A first ordering was done when creating the
        # relevant stakeholders. However, it is necessary to restore this
        # ordering after all the additional data was added through this query.
        if get_current_order_direction(self.request) == 'desc':
            query = query.order_by(desc(relevant_query.c.order_value))
        else:
            query = query.order_by(asc(relevant_query.c.order_value))

        if with_metadata is True:
            query = query.add_columns(
                Stakeholder.previous_version.label('previous_version'),
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
            # Activity involved with the relevant Stakeholders
            latest_filter = self.Session.query(
                Activity.activity_identifier,
                Involvement.fk_stakeholder,
                func.max(Activity.version).label('max_version')
            ).\
                join(Involvement).\
                join(
                    relevant_query, relevant_query.c.order_id
                    == Involvement.fk_stakeholder).\
                group_by(
                    Activity.activity_identifier, Involvement.fk_stakeholder).\
                subquery()

            inv_status = self.Session.query(
                Activity.id.label('activity_id'),
                Activity.activity_identifier.label('activity_identifier'),
                Activity.fk_status.label('activity_status'),
                Activity.version.label('activity_version'),
                Activity.fk_changeset.label('changeset_id')
            ).\
                filter(Activity.fk_status.in_(involvement_status_ids)).\
                join(Involvement).\
                join(latest_filter, and_(
                    latest_filter.c.max_version == Activity.version,
                    latest_filter.c.activity_identifier
                    == Activity.activity_identifier,
                    latest_filter.c.fk_stakeholder
                    == Involvement.fk_stakeholder
                )).\
                subquery()
            inv_query = self.Session.query(
                Involvement.fk_stakeholder.label('stakeholder_id'),
                Stakeholder_Role.id.label('role_id'),
                Stakeholder_Role.name.label('role_name'),
                Changeset.fk_user.label('activity_user_id'),
                inv_status.c.activity_identifier.label(
                    'activity_identifier'),
                inv_status.c.activity_status.label('activity_status'),
                inv_status.c.activity_version.label('activity_version')
            ).\
                join(inv_status,
                     inv_status.c.activity_id == Involvement.fk_activity).\
                join(Changeset, Changeset.id == inv_status.c.changeset_id).\
                join(Stakeholder_Role).\
                subquery()

            query = query.\
                add_columns(
                    inv_query.c.activity_identifier.
                    label('activity_identifier'),
                    inv_query.c.role_name.label('stakeholder_role'),
                    inv_query.c.role_id.label('stakeholder_role_id'),
                    inv_query.c.activity_status.label('activity_status'),
                    inv_query.c.activity_version.label('activity_version'),
                    inv_query.c.activity_user_id.label('activity_user_id')
                ).\
                outerjoin(
                    inv_query,
                    inv_query.c.stakeholder_id == Stakeholder.id)

        if return_count:
            return query, count
        else:
            return query

    def query_to_features(
            self, query, involvements='none', public_query=False,
            translate=True):
        """
        TODO
        """
        logged_in, is_moderator = get_user_privileges(self.request)

        features = []
        for q in query.all():

            # Prepare values if needed
            identifier = str(q.identifier)
            taggroup_id = int(q.taggroup) if q.taggroup is not None else None
            key = q.key
            value = q.value
            if translate is not False:
                if q.key_translated is not None:
                    key = q.key_translated
                if q.value_translated is not False:
                    value = q.value_translated

            # Use UID and version to find existing Feature or create a new one
            feature = None
            for f in features:
                if (f.identifier == identifier and f.version == q.version
                        and f.order_value == q.order_value):
                    feature = f

            if feature is None:
                feature = ItemFeature(
                    identifier, q.order_value, q.version, q.status_id)

                # TODO: Create separate function with this
                feature.status = getattr(q, 'status', None)
                feature.timestamp = getattr(q, 'timestamp', None)
                feature.previous_version = getattr(
                    q, 'previous_version', None)
                feature.user_id = getattr(q, 'userid', None)
                feature.user_name = getattr(q, 'user_name', None)
                feature.user_privacy = getattr(q, 'user_privacy', None)
                feature.user_firstname = getattr(q, 'user_firstname', None)
                feature.user_lastname = getattr(q, 'user_lastname', None)
                feature.institution_id = getattr(q, 'institution_id', None)
                feature.institution_name = getattr(
                    q, 'institution_name', None)
                feature.institution_url = getattr(q, 'institution_url', None)
                feature.institution_logo = getattr(
                    q, 'institution_logo', None)

                features.append(feature)

            # Check if current Taggroup is already present in the Feature
            taggroup = feature.get_taggroup_by_id(taggroup_id)
            if taggroup is None and key is not None:
                taggroup = ItemTaggroup(taggroup_id, q.tg_id, q.main_tag)
                feature.add_taggroup(taggroup)

            # Because of Involvements, the same Tags appears for each
            # Involvement, so add it only once to TagGroup
            if taggroup is not None and taggroup.get_tag_by_id(q.tag) is None:
                taggroup.add_tag(ItemTag(q.tag, key, value))

            # Involvements
            if involvements != 'none':
                # TODOs

                try:
                    if q.activity_identifier is not None:

                        try:
                            request_user_id = self.request.user.id
                        except AttributeError:
                            request_user_id = None

                        newer_pending_exists = False
                        if q.activity_status == 1:
                            for p_i in feature._involvements:
                                if (p_i.get_guid() == q.activity_identifier
                                        and p_i.get_status() == 1):
                                    if p_i.get_version() > q.activity_version:
                                        newer_pending_exists = True
                                    else:
                                        feature.remove_involvement(p_i)

                        # Flag indicating if Involvement to this Activity is
                        # not yet found ('none') or not to be added ('false')
                        inv = self._flag_add_involvement(
                            feature, q.status_id, q.activity_status,
                            q.activity_identifier, q.activity_version,
                            q.activity_user_id, q.stakeholder_role,
                            request_user_id, public_query, logged_in,
                            is_moderator)

                        if inv is None and newer_pending_exists is False:
                            # Create new Involvement and add it to Stakeholder
                            # Default: only basic information about Involvement
                            feature.add_involvement(Inv(
                                q.activity_identifier, None,
                                q.stakeholder_role, q.stakeholder_role_id,
                                q.activity_version, q.activity_status))

                except ValueError:
                    pass

        if involvements == 'full':
            # TODO

            # If full involvements are to be shown, collect the identifiers and
            # versions of each Activity and prepare a dict. Query the details
            # (Tag Groups) of these Activities using the ActivityProtocol and
            # replace the existing Involvements. Query them all at once to
            # improve performance.

            inv_dicts = []
            for stakeholder in features:
                for i in stakeholder._involvements:
                    inv_dicts.append({
                                     'identifier': i.get_guid(),
                                     'version': i.get_version()
                                     })

            # Use ActivityProtocol to query the details of the Activities
            from lmkp.views.activity_protocol3 import ActivityProtocol3
            ap = ActivityProtocol3(self.Session)
            relevant_activities = ap._get_relevant_activities_dict(
                self.request, inv_dicts)

            a_query = ap._query_many(self.request, relevant_activities,
                                     involvements=False, return_count=False)
            activities = ap._query_to_activities(self.request, a_query,
                                                 involvements='none')

            # Loop through all existing Involvements
            for stakeholder in features:
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
                            i.get_guid(), activity, i.get_role(),
                            i.get_role_id(), i.get_version(), i.get_status())

        return features
