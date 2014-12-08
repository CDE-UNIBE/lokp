from pyramid.httpexceptions import HTTPBadRequest
from sqlalchemy import func
from sqlalchemy.sql.expression import (
    and_,
    asc,
    desc,
    or_,
    select,
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
    InvolvementFeature,
    ItemFeature,
    ItemTag,
    ItemTaggroup,
)
from lmkp.protocols.protocol import Protocol
from lmkp.views.views import (
    get_current_logical_filter_operator,
    get_current_order_direction,
    get_current_involvement_details,
    get_current_limit,
    get_current_offset,
    get_current_version,
)


class StakeholderProtocol(Protocol):
    """
    The StakeholderProtocol handles all query and create operations with
    the :term:`Stakeholders`.

    Inherits from:
        :class:`lmkp.protocols.protocol.Protocol`
    """

    def read_one(self, uid, public_query=True, translate=True):
        """
        Read one single :term:`Stakeholder` version: Either latest
        version visible by the current user or the version indicated if
        it exists and is visible.This function handles the query,
        creates and returns the Feature.

        Args:
            ``uid`` (str): The :term:`UUID` of the :term:`Stakeholder`
            to query.

            ``public_query`` (bool): An optional boolean indicating
            whether to return only a version visible to the public (eg.
            no pending) or not. Defaults to ``True``.

            ``translate`` (bool): An optional boolean indicating whether
            to return translated values or not. Defaults to ``True``.

        Returns:
            ``dict``. The :term:`Activity` Feature in JSON compatible
            format or ``{}`` if no version was found.
        """
        version = get_current_version(self.request)
        relevant_query = self.get_relevant_query_one(
            uid, version=version, public_query=public_query)

        involvement_details = get_current_involvement_details(self.request)
        show_involvements = involvement_details != 'none'

        # Limit and offset are fix
        limit = 1
        offset = None

        query = self.query_many(
            relevant_query, limit=limit, offset=offset, return_count=False,
            with_involvements=show_involvements)

        features = self.query_to_features(
            query, involvements=involvement_details, public_query=public_query,
            translate=translate)

        if len(features) == 0:
            return {}

        return features[0].to_json(self.request)

    def read_many(
            self, public_query=True, limit=None, offset=None, translate=True,
            other_identifiers=None):
        """
        Read many :term:`Stakeholders`. This function handles the query,
        applies filters, creates and returns the Features.

        Args:
            ``public_query`` (bool): An optional boolean indicating
            whether to return only versions visible to the public (eg.
            no pending) or not. Defaults to``True``.

            ``limit`` (int): An optional limit. If no limit is provided,
            the one from the request is used if available.

                .. seealso::
                   :class:`lmkp.views.views.get_current_limit`

            ``offset`` (int): An optional offset. If no offset it
            provided, the one from the reuqest is used if available.

                .. seealso::
                   :class:`lmkp.views.views.get_current_offset`

            ``translate`` (bool): An optional boolean indicating whether
            to return translated values or not. Defaults to ``True``.

            ``other_identifiers`` (list or None): A list of
            :term:`Activity` identifiers to filter the
            :term:`Stakeholders` by. If ``None``, no filter is applied.
            If an empty list is provided, the :term:`Stakeholders` are
            filtered to show only those involved in currently visible
            :term:`Activities`. If a list with identifiers is provided,
            the :term:`Stakeholders` are filtered to include only those
            involved in these :term:`Activities`. Defaults to ``None``.

        Returns:
            ``dict``. A dictionary containing the total count of the
            query and the :term:`Stakeholder` Features in JSON
            compatible format.

                .. seealso::
                   :class:`lmkp.protocols.features.ItemFeature.to_json`
        """
        relevant_query = self.get_relevant_query_many(
            public_query=public_query, other_identifiers=other_identifiers)

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
        Get a query with the database IDs of relevant
        :term:`Stakeholders` based on a list of dicts containing the
        identifier and version of :term:`Stakeholders`. No additional
        filters are applied.

        Args:
            ``stakeholder_list`` (list): A list of dicts. Each dict
            contains the ``identifier`` and ``version`` of a
            :term:`Stakeholder`.

        Returns:
            ``sqlalchemy.orm.query.Query``. A SQLAlchemy Query
            containing namely the IDs of the filtered (relevant)
            :term:`Stakeholders`.
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

    def get_relevant_query_one(self, uid, version=None, public_query=False):
        """
        Get a query with the database ID of a single relevant
        :term:`Stakeholder` version.

        Args:
            ``uid`` (str): The :term:`UUID` of the :term:`Stakeholder`
            to query.

            ``version`` (int): An optional version of the
            :term:`Stakeholder` to query. If provided, a filter is set to
            this version though it may not be visible to the current
            user because of its status. If set to ``None``, no version
            filter is applied and the latest visible version is
            returned. Defaults to ``None``.

            ``public_query`` (bool): An optional boolean indicating
            whether to return only a version visible to the public (eg.
            no pending) or not. Defaults to ``True``.

        Returns:
            ``sqlalchemy.orm.query.Query``. A SQLAlchemy Query
            containing namely the ID of the filtered (relevant)
            :term:`Stakeholder`.
        """
        # Prepare order: Get the order from request
        order_query = self.get_order('sh')

        relevant_query = self.Session.query(
            Stakeholder.id.label('order_id'),
            order_query.c.value.label('order_value'),
            Stakeholder.fk_status,
            Stakeholder.stakeholder_identifier,
            Stakeholder.version
        ).\
            filter(Stakeholder.identifier == uid)

        # Join Stakeholders with TagGroups
        relevant_query = relevant_query.\
            outerjoin(SH_Tag_Group)

        # Join Stakeholders with order and group
        relevant_query = relevant_query.\
            outerjoin(order_query, order_query.c.id == Stakeholder.id)
        relevant_query = relevant_query.order_by(asc(order_query.c.value))
        relevant_query = relevant_query.\
            group_by(
                Stakeholder.id, order_query.c.value,
                Stakeholder.fk_status, Stakeholder.stakeholder_identifier)

        if version is None:
            # Decide which version is visible by default based on status
            # filter and user privileges.
            relevant_query = self.apply_visible_version_filter(
                'sh', relevant_query, public_query=public_query)
        else:
            # Decide which versions are visible and filter out the one
            # requested.
            relevant_query = self.apply_many_visible_version_filter(
                'sh', relevant_query, public_query=public_query)
            relevant_query = relevant_query.filter(
                Stakeholder.version == version)

        return relevant_query

    def get_relevant_query_many(
            self, filter=None, public_query=False, other_identifiers=None):
        """
        Get a query with the database IDs of relevant
        :term:`Stakeholders` based on the various filters (attributes on
        both :term:`Stakeholders` and :term:`Activities`,
        :term:`Status`, :term:`Profile` etc.) which are currently set.

        Args:
            ``filter`` (dict): An optional dictionary with custom
            filters, overwriting the ones from the request. Valid
            entries for the dict are ``a_tag_filters`` and
            ``sh_tag_filters``.

            ``public_query`` (bool): An optional boolean indicating
            whether to return only versions visible to the public (eg.
            no pending) or not.

            ``other_identifiers`` (list or None): A list of
            :term:`Activity` identifiers to filter the
            :term:`Stakeholders` by. If ``None``, no filter is applied.
            If an empty list is provided, the :term:`Stakeholders` are
            filtered to show only those involved in currently visible
            :term:`Activities`. If a list with identifiers is provided,
            the :term:`Stakeholders` are filtered to include only those
            involved in these :term:`Activities`. Defaults to ``None``.

        Returns:
            ``sqlalchemy.orm.query.Query``. A SQLAlchemy Query
            containing namely the IDs of the filtered (relevant)
            :term:`Stakeholders`.
        """
        logged_in, is_moderator = get_user_privileges(self.request)

        # Filter: If no custom filter was provided, get filters from request
        if filter is None:
            a_tag_filters, sh_tag_filters = self.get_attribute_filters()
        else:
            a_tag_filters = filter.get('a_tag_filters', [])
            sh_tag_filters = filter.get('sh_tag_filters', [])

        # Prepare order: Get the order from request
        order_query = self.get_order('sh')

        relevant_query = self.Session.query(
            Stakeholder.id.label('order_id'),
            order_query.c.value.label('order_value'),
            Stakeholder.fk_status,
            Stakeholder.stakeholder_identifier
        )

        if other_identifiers is not None:
            # Use the ActivityProtocol to query relevant Activities
            from lmkp.protocols.activity_protocol import ActivityProtocol
            ap = ActivityProtocol(self.request)

            if len(other_identifiers) == 0:
                # No identifiers specified, query many
                relevant_others = ap.get_relevant_query_many(
                    public_query=public_query)
            elif len(other_identifiers) == 1:
                # Query only one
                raise Exception('TODO')
            else:
                raise HTTPBadRequest(detail='Not yet supported')

            relevant_others = relevant_others.subquery()
            relevant_query = relevant_query.\
                join(Involvement).\
                filter(Involvement.fk_activity.in_(
                    select([relevant_others.c.order_id])))

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
            """
            Use the ActivityProtocol to query the IDs of the Activities
            which pass the filter. Only the IDs are important, no need
            to query all the taggroups and tags.
            """
            filter_dict = {
                'a_tag_filters': a_tag_filters
            }
            from lmkp.protocols.activity_protocol import ActivityProtocol
            ap = ActivityProtocol(self.request)
            a_relevant_query = ap.get_relevant_query_many(
                filter=filter_dict, public_query=public_query)
            a_query = ap.query_many_only_id(a_relevant_query)
            a_subquery = a_query.subquery()
            if get_current_logical_filter_operator(self.request) == 'or':
                # OR: use 'union' to add id's to relevant_stakeholders
                relevant_query = relevant_query.\
                    union(
                        self.Session.query(
                            Stakeholder.id.label('order_id'),
                            Changeset.timestamp.label('order_value'),
                            Stakeholder.fk_status,
                            Stakeholder.stakeholder_identifier
                        ).
                        join(Changeset).
                        join(Involvement).
                        join(
                            a_subquery, a_subquery.c.id
                            == Involvement.fk_activity).
                        group_by(
                            Stakeholder.id, Changeset.timestamp,
                            Stakeholder.fk_status,
                            Stakeholder.stakeholder_identifier))
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

    def query_many_only_id(self, relevant_query):
        """
        Extend a subquery of relevant :term:`Stakeholder` IDs to contain
        only the IDs of the :term:`Stakeholders`. In contrary to
        :class:`query_many`, this function does not add any attributes
        at all.

        Args:
            ``relevant_query`` (sqlalchemy.orm.query.Query): A
            SQLAlchemy containing the filtered (relevant)
            :term:`Stakeholder` IDs.

            .. seealso::
               :class:`get_relevant_query_many`

        Returns:
            ``sqlalchemy.orm.query.Query``. A SQLAlchemy Query for the
            :term:`Stakeholders`.
        """
        relevant_query = relevant_query.subquery()
        query = self.Session.query(
            Stakeholder.id.label('id')
        ).\
            join(relevant_query,
                 relevant_query.c.order_id == Stakeholder.id)
        return query

    def query_many(
            self, relevant_query, limit=None, offset=None,
            with_involvements=False, return_count=True,
            with_metadata=False):
        """
        Extend a subquery of relevant :term:`Stakeholder` IDs to get a
        complete query object for the :term:`Stakeholders`. This does
        not actually perform a query (except a SQL count if requested)
        but rather creates and returns a query joining the relevant IDs
        with all its attributes and involvements.

        Args:
            ``relevant_query`` (sqlalchemy.orm.query.Query): A
            SQLAlchemy containing the filtered (relevant)
            :term:`Stakeholder` IDs.

            .. seealso::
               :class:`get_relevant_query_many`

            ``limit`` (int or None): An optional integer with the limit
            to be applied to the query.

            ``offset`` (int or None): An optional integer with the
            offset to be applied to the query.

            ``with_involvements`` (bool): An optional boolean indicating
            whether to include :term:`Involvements` in the query or not.
            If true, additional columns for the attributes of the
            :term:`Activities` are added to the query. Defaults to
            ``false``.

            ``return_count`` (bool): An optional boolean indicating
            whether to return the count of the query along with the
            query. The count happens before the limit and offset are
            applied, it therefore returns the total count of the entire
            query. Defaults to ``true``.

            ``with_metadata`` (bool): An optional boolean indicating
            whether to include metadata (eg. about the user and
            institution creating the version) for the
            :term:`Stakeholders` or not. Defaults to ``false``.

        Returns:
            ``sqlalchemy.orm.query.Query``. A SQLAlchemy Query for the
            :term:`Stakeholders`.

            ``long``. (only if ``return_count=True``) The total count of
            the query.
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
                User.username.label('activity_username'),
                inv_status.c.activity_identifier.label(
                    'activity_identifier'),
                inv_status.c.activity_status.label('activity_status'),
                inv_status.c.activity_version.label('activity_version')
            ).\
                join(inv_status,
                     inv_status.c.activity_id == Involvement.fk_activity).\
                join(Changeset, Changeset.id == inv_status.c.changeset_id).\
                join(User, User.id == Changeset.fk_user).\
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
                    inv_query.c.activity_username.label('activity_username')
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
        Transform the query to features. Every value of each
        :term:`Stakeholder` is a line of the query. These attributes
        have to be collected to form an StakeholderFeature. Also add
        involvement to the features.

        Args:
            ``query`` (sqlalchemy.orm.query.Query): A SQLAlchemy Query
            for the :term:`Stakeholders`.

            ``involvements`` (str): The detail level of the
            involvements. If ``none``, no involvements are added to the
            feature. If ``full``, the :term:`Stakeholder` features is
            added to the involvements. Otherwise, only an involvement
            with the basic information is added. Defaults to ``none``.

                .. seealso::
                   :class:`lmkp.views.views.get_current_involvement_details`

            ``public_query`` (bool): An optional boolean indicating
            whether to return only versions visible to the public (eg.
            no pending) or not. Defaults to``False``.

            ``translate`` (bool): An optional boolean indicating whether
            to return translated values or not. Defaults to ``True``.

        Returns:
            ``list``. A list of
            :class:`lmkp.protocols.activity_features.ActivityFeature`.
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
                if q.value_translated is not None:
                    value = q.value_translated

            # Use UID and version to find existing Feature or create a new one
            feature = None
            for f in features:
                if (f.identifier == identifier and f.version == q.version
                        and f.order_value == q.order_value):
                    feature = f

            if feature is None:
                feature = ItemFeature(
                    q.id, identifier, q.order_value, q.version, q.status_id)

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
            if involvements != 'none' and q.activity_identifier is not None:

                involvement = InvolvementFeature(
                    q.activity_identifier, q.activity_version,
                    q.activity_status, q.stakeholder_role,
                    q.stakeholder_role_id, q.activity_username)

                feature.add_or_replace_involvement(
                    involvement, self.request, public_query=public_query)

        if involvements == 'full':
            """
            If full involvements are to be shown, collect the
            identifiers and versions of each Activity as dict and
            prepare a list. Query the details (Taggroups) of these
            Activities using the ActivityProtocol and replace the
            existing Involvements. Query them all at once to improve
            performance.
            """
            involvement_dicts = []
            for feature in features:
                for inv in feature.involvements:
                    involvement_dicts.append({
                        'identifier': inv.identifier,
                        'version': inv.version
                    })
            from lmkp.protocols.activity_protocol import ActivityProtocol
            ap = ActivityProtocol(self.request)
            relevant_query = ap.get_relevant_query_from_list(involvement_dicts)
            a_query = ap.query_many(
                relevant_query, with_involvements=False, return_count=False)
            a_features = ap.query_to_features(a_query, involvements='none')

            # TODO: There might be some improvements possible here
            for sh_feature in features:
                for a_feature in a_features:
                    inv = sh_feature.get_involvement_by_identifier_version(
                        a_feature.identifier, a_feature.version)
                    if inv is not None:
                        inv.feature = a_feature

        return features
