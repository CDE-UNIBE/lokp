from geoalchemy import WKBSpatialElement
from geoalchemy.functions import functions as geofunctions
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.security import authenticated_userid
from shapely.geometry.polygon import Polygon
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
    A_Key,
    A_Value,
    A_Tag,
    A_Tag_Group,
    Activity,
    Changeset,
    Institution,
    Involvement,
    Profile,
    Stakeholder,
    Stakeholder_Role,
    Status,
    User,
)
from lmkp.protocols.activity_features import (
    ActivityFeature,
    ActivityTaggroup,
)
from lmkp.protocols.features import (
    ItemTag,
    InvolvementFeature,
)
from lmkp.protocols.protocol import Protocol
from lmkp.utils import validate_bbox
from lmkp.views.translation import get_translated_keys
from lmkp.views.views import (
    get_bbox_parameters,
    get_current_profile,
    get_current_logical_filter_operator,
    get_current_order_direction,
    get_current_involvement_details,
    get_current_limit,
    get_current_offset,
    get_current_translation_parameter,
    get_current_attributes,
    get_current_locale,
    get_current_taggroup_geometry_parameter,
    get_current_version,
)


class ActivityProtocol(Protocol):
    """
    The ActivityProtocol handles all query and create operations with
    the :term:`Activities`.

    Inherits from:
        :class:`lmkp.protocols.protocol.Protocol`
    """

    def read_one(self, uid, public_query=True, translate=True):
        """
        Read one single :term:`Activity` version: Either latest version
        visible by the current user or the version indicated if it
        exists and is visible.This function handles the query, creates
        and returns the Feature.

        Args:
            ``uid`` (str): The :term:`UUID` of the :term:`Activity` to
            query.

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
        Read many :term:`Activities`. This function handles the query,
        applies filters, creates and returns the Features.

        Args:
            ``public_query`` (bool): An optional boolean indicating
            whether to return only versions visible to the public (eg.
            no pending) or not. Defaults to ``True``.

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
            :term:`Stakeholder` identifiers to filter the
            :term:`Activities` by. If ``None``, no filter is applied. If
            a list with identifiers is provided, the :term:`Activities`
            are filtered to include only those involved in these
            :term:`Stakeholders`. Defaults to ``None``.

        Returns:
            ``dict``. A dictionary containing the total count of the
            query and the :term:`Activity` Features in JSON compatible
            format.

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

    def read_many_geojson(self, public_query=True):
        """
        Read many :term:`Activities` and return them in a GeoJSON
        compatible representation. This function handles the query,
        applies filters, creates and returns the Features.

        The focus is on a GeoJSON representation and this function does
        not return full Taggroups, only selected attributes.

        Args:
            ``public_query`` (bool): An optional boolean indicating
            whether to return only versions visible to the public (eg.
            no pending) or not. Defaults to ``True``.

        Returns:
            ``dict``. A dictionary containing the :term:`Activity`
            Features in a GeoJSON compatible format.

                .. seealso::
                   |to_geojson|

        .. |to_geojson| replace::
           :func:`lmkp.protocols.activity_features.ActivityFeature.to_geojson`
        """
        relevant_query = self.get_relevant_query_many(
            public_query=public_query, bbox_cookies=False)

        limit = get_current_limit(self.request)
        offset = get_current_offset(self.request)
        translate = get_current_translation_parameter(self.request)
        attributes = get_current_attributes(self.request)
        translated_attributes = get_translated_keys(
            'a', attributes, get_current_locale(self.request))
        taggroup_geometry = get_current_taggroup_geometry_parameter(
            self.request)

        query = self.query_many_geojson(
            relevant_query, limit=limit, offset=offset,
            attributes=translated_attributes,
            taggroup_geometry=taggroup_geometry, translate=translate)

        return self.query_to_geojson(query)

    def get_relevant_query_from_list(self, activity_list):
        """
        Get a query with the database IDs of relevant :term:`Activities`
        based on a list of dicts containing the identifier and version
        of :term:`Activities`. No additional filters are applied.

        Args:
            ``activity_list`` (list): A list of dicts. Each dict
            contains the ``identifier`` and ``version`` of a
            :term:`Activity`.

        Returns:
            ``sqlalchemy.orm.query.Query``. A SQLAlchemy Query
            containing namely the IDs of the filtered (relevant)
            :term:`Activities`.
        """
        # Prepare filters with the dict
        dict_filter = []
        for a in activity_list:
            dict_filter.append(and_(
                Activity.activity_identifier == a.get('identifier'),
                Activity.version == a.get('version')))

        # Prepare order: Get the order from request
        order_query = self.get_order('a')

        relevant_query = self.Session.query(
            Activity.id.label('order_id'),
            order_query.c.value.label('order_value'),
            Activity.fk_status,
            Activity.activity_identifier
        ).filter(or_(* dict_filter))

        # Join Stakeholders with Taggroups and order_query, then group it
        relevant_query = relevant_query.\
            outerjoin(A_Tag_Group).\
            outerjoin(order_query, order_query.c.id == Activity.id).\
            group_by(
                Activity.id, order_query.c.value, Activity.fk_status,
                Activity.activity_identifier)

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
        :term:`Activity` version.

        Args:
            ``uid`` (str): The :term:`UUID` of the :term:`Activity` to
            query.

            ``version`` (int): An optional version of the
            :term:`Activity` to query. If provided, a filter is set to
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
            :term:`Activity`.
        """
        # Prepare order: Get the order from request
        order_query = self.get_order('a')

        relevant_query = self.Session.query(
            Activity.id.label('order_id'),
            order_query.c.value.label('order_value'),
            Activity.fk_status,
            Activity.activity_identifier,
            Activity.version
        ).\
            filter(Activity.identifier == uid)

        # Join Activities with TagGroups
        relevant_query = relevant_query.\
            outerjoin(A_Tag_Group)

        # Join Activities with order and group
        relevant_query = relevant_query.\
            outerjoin(order_query, order_query.c.id == Activity.id)
        relevant_query = relevant_query.order_by(asc(order_query.c.value))
        relevant_query = relevant_query.\
            group_by(Activity.id, order_query.c.value, Activity.fk_status,
                     Activity.activity_identifier)

        if version is None:
            # Decide which version is visible by default based on status
            # filter and user privileges.
            relevant_query = self.apply_visible_version_filter(
                'a', relevant_query, public_query=public_query)
        else:
            # Decide which versions are visible and filter out the one
            # requested.
            relevant_query = self.apply_many_visible_version_filter(
                'a', relevant_query, public_query=public_query)
            relevant_query = relevant_query.filter(Activity.version == version)

        return relevant_query

    def get_relevant_query_many(
            self, filter=None, public_query=False, bbox_cookies=True,
            other_identifiers=None):
        """
        Get a query with the database IDs of relevant :term:`Activities`
        based on the various filters (attributes on both
        :term:`Activities` and :term:`Stakeholders`, :term:`Status`,
        :term:`Profile` etc.) which are currently set.

        Args:
            ``filter`` (dict): An optional dictionary with custom
            filters, overwriting the ones from the request. Valid
            entries for the dict are ``a_tag_filters`` and
            ``sh_tag_filters``.

            ``public_query`` (bool): An optional boolean indicating
            whether to return only versions visible to the public (eg.
            no pending) or not.

            ``bbox_cookies`` (bool): An optional boolean indicating
            whether to look for a location cookie as fallback if no
            request parameters were provided. This argument is passed to
            the `get_bbox_parameters` function.

            .. seealso::
               :class:`lmkp.views.views.get_bbox_parameters`

            ``other_identifiers`` (list or None): A list of
            :term:`Stakeholder` identifiers to filter the
            :term:`Activities` by. If ``None``, no filter is applied. If
            a list with identifiers is provided, the :term:`Activities`
            are filtered to include only those involved in these
            :term:`Stakeholders`. Defaults to ``None``.

        Returns:
            ``sqlalchemy.orm.query.Query``. A SQLAlchemy Query
            containing namely the IDs of the filtered (relevant)
            :term:`Activities`.
        """
        logged_in, is_moderator = get_user_privileges(self.request)

        # Filter: If no custom filter was provided, get filters from request
        if filter is None:
            a_tag_filters, sh_tag_filters = self.get_attribute_filters()
        else:
            a_tag_filters = filter.get('a_tag_filters', [])
            sh_tag_filters = filter.get('sh_tag_filters', [])

        # Prepare order: Get the order from request
        order_query = self.get_order('a')

        relevant_query = self.Session.query(
            Activity.id.label('order_id'),
            order_query.c.value.label('order_value'),
            Activity.fk_status,
            Activity.activity_identifier
        )

        if other_identifiers is not None:
            # Use the StakeholderProtocol to query relevant Stakeholders
            from lmkp.protocols.stakeholder_protocol import StakeholderProtocol
            sp = StakeholderProtocol(self.request)

            if len(other_identifiers) == 1:
                # Query only one
                relevant_others = None
                raise Exception('TODO')
            elif isinstance(other_identifiers, list):
                raise HTTPBadRequest(detail='Not yet supported')

            relevant_others = relevant_others.subquery()
            relevant_query = relevant_query.\
                join(Involvement).\
                filter(Involvement.fk_stakeholder.in_(
                    select([relevant_others.c.order_id])))

        # Activity attribute filters
        filter_subquery = None
        if len(a_tag_filters) == 0:
            pass
        elif get_current_logical_filter_operator(self.request) == 'or':
            """
            Logical "or" filter: Use subqueries to collect the IDs of
            all Items matching each filter. Perform a SQL UNION based on
            the first subquery to unite all other subqueries and put all
            Item IDs together.
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
            relevant_query = relevant_query.\
                join(filter_subquery,
                     filter_subquery.c.a_filter_id == Activity.id)
        else:
            # If no filter was provided, simply join with A_Tag_Group (outer
            # join to also capture empty Items)
            relevant_query = relevant_query.\
                outerjoin(A_Tag_Group)

        # Always filter by profile boundary
        relevant_query = relevant_query.\
            filter(self.get_profile_filter())

        # Filter spatially
        relevant_query = relevant_query.\
            filter(self.get_bbox_filter(cookies=bbox_cookies))

        # Join Activities with order and group
        relevant_query = relevant_query.\
            outerjoin(order_query, order_query.c.id == Activity.id)

        # Decide which version is based on status filter and user
        # privileges.
        relevant_query = self.apply_visible_version_filter(
            'a', relevant_query, public_query=public_query)

        relevant_query = relevant_query.\
            group_by(Activity.id, order_query.c.value, Activity.fk_status,
                     Activity.activity_identifier)

        # Filter based on Stakeholder attributes
        if len(sh_tag_filters) > 0:
            """
            Use the StakeholderProtocol to query the IDs of the
            Stakeholders which pass the filter. Only the IDs are
            important, no need to query all the taggroups and tags.
            """
            filter_dict = {
                'sh_tag_filters': sh_tag_filters
            }
            from lmkp.protocols.stakeholder_protocol import StakeholderProtocol
            sp = StakeholderProtocol(self.request)
            sh_relevant_query = sp.get_relevant_query_many(
                filter=filter_dict, public_query=public_query)
            sh_query = sp.query_many_only_id(sh_relevant_query)
            sh_subquery = sh_query.subquery()
            if get_current_logical_filter_operator(self.request) == 'or':
                # OR: use 'union' to add id's to relevant_query
                relevant_query = relevant_query.\
                    union(
                        self.Session.query(
                            Activity.id.label('order_id'),
                            Changeset.timestamp.label('order_value'),
                            Activity.fk_status,
                            Activity.activity_identifier
                        ).
                        join(Changeset).
                        join(Involvement).
                        join(
                            sh_subquery, sh_subquery.c.id ==
                            Involvement.fk_stakeholder).
                        group_by(
                            Activity.id, Changeset.timestamp,
                            Activity.fk_status, Activity.activity_identifier))
            else:
                # AND: filter id's of relevant_query
                relevant_query = relevant_query.\
                    join(Involvement).\
                    join(sh_subquery, sh_subquery.c.id ==
                         Involvement.fk_stakeholder).\
                    group_by(Activity.id)

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
        Extend a subquery of relevant :term:`Activity` IDs to contain
        only the IDs of the :term:`Activities`. In contrary to
        :class:`query_many`, this function does not add any attributes
        at all.

        Args:
            ``relevant_query`` (sqlalchemy.orm.query.Query): A
            SQLAlchemy containing the filtered (relevant)
            :term:`Activity` IDs.

            .. seealso::
               :class:`get_relevant_query_many`

        Returns:
            ``sqlalchemy.orm.query.Query``. A SQLAlchemy Query for the
            :term:`Activities`.
        """
        relevant_query = relevant_query.subquery()
        query = self.Session.query(
            Activity.id.label('id')
        ).\
            join(relevant_query,
                 relevant_query.c.order_id == Activity.id)
        return query

    def query_many(
            self, relevant_query, limit=None, offset=None,
            with_involvements=False, return_count=True,
            with_metadata=False):
        """
        Extend a subquery of relevant :term:`Activity` IDs to get a
        complete query object for the :term:`Activities`. This does not
        actually perform a query (except a SQL count if requested) but
        rather creates and returns a query joining the relevant IDs with
        all its attributes and involvements.

        Args:
            ``relevant_query`` (sqlalchemy.orm.query.Query): A
            SQLAlchemy containing the filtered (relevant)
            :term:`Activity` IDs.

            .. seealso::
               :class:`get_relevant_query_many`

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
            count = relevant_query.count()

        # Apply limit and offset
        if limit is not None:
            relevant_query = relevant_query.limit(limit)
        if offset is not None:
            relevant_query = relevant_query.offset(offset)

        # Create query
        relevant_query = relevant_query.subquery()
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
            relevant_query.c.order_value.label('order_value')
        ).\
            join(relevant_query,
                 relevant_query.c.order_id == Activity.id).\
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
            query = query.order_by(desc(relevant_query.c.order_value))
        else:
            query = query.order_by(asc(relevant_query.c.order_value))

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
                join(relevant_query, relevant_query.c.order_id ==
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
                User.username.label('stakeholder_username'),
                inv_status.c.stakeholder_identifier.
                label('stakeholder_identifier'),
                inv_status.c.stakeholder_status.label('stakeholder_status'),
                inv_status.c.stakeholder_version.
                label('stakeholder_version')
            ).\
                join(inv_status, inv_status.c.stakeholder_id ==
                     Involvement.fk_stakeholder).\
                join(Changeset, Changeset.id == inv_status.c.changeset_id).\
                join(User, User.id == Changeset.fk_user).\
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
                    inv_query.c.stakeholder_username.label(
                        'stakeholder_username')
                ).\
                outerjoin(inv_query, inv_query.c.activity_id == Activity.id)

        if return_count:
            return query, count
        else:
            return query

    def query_many_geojson(
            self, relevant_query, limit=None, offset=None, attributes=[],
            taggroup_geometry=False, translate=True):
        """
        Extend a subquery of relevant :term:`Activity` IDs to get a
        complete query object for the GeoJSON representation of
        :term:`Activities`. This does not perform a query but rather
        creates a query joining the relevant IDs with the optional
        attributes.

        Args:
            ``relevant_query`` (sqlalchemy.orm.query.Query): A
            SQLAlchemy containing the filtered (relevant)
            :term:`Activity` IDs.

            .. seealso::
               :class:`get_relevant_query_many`

            ``limit`` (int or None): An optional integer with the limit
            to be applied to the query.

            ``offset`` (int or None): An optional integer with the
            offset to be applied to the query.

            ``attributes`` (list): An optional list with
            :term:`Activity` attributes to add to the query. By default,
            the GeoJSON representation does not include any attributes.

            ``taggroup_geometry`` (bool): An optional boolean indicating
            whether to include the geometries of Taggroups or not.
            Defaults to ``False``.

            ``translate`` (bool): An optional boolean indicating whether
            to translate the selected ``attributes`` or not. Defaults to
            ``True``.

        Returns:
            ``sqlalchemy.orm.query.Query``. A SQLAlchemy Query for the
            :term:`Activities`.
        """
        # Apply limit and offset
        if limit is not None:
            relevant_query = relevant_query.limit(limit)
        if offset is not None:
            relevant_query = relevant_query.offset(offset)

        # Create query
        relevant_query = relevant_query.subquery()
        query = self.Session.query(
            Activity.id.label('id'),
            Activity.point.label('geometry'),
            Activity.activity_identifier.label('identifier'),
            Activity.version.label('version'),
            Status.id.label('status_id'),
            Status.name.label('status_name')
        ).\
            join(relevant_query,
                 relevant_query.c.order_id == Activity.id).\
            join(Status)

        if len(attributes) > 0:
            original_attributes = [a[0] for a in attributes]
            query = query.\
                add_columns(
                    A_Value.value.label('value'),
                    A_Key.key.label('key')
                ).\
                outerjoin(
                    A_Tag_Group, Activity.id == A_Tag_Group.fk_activity).\
                outerjoin(A_Tag, A_Tag_Group.id == A_Tag.fk_a_tag_group).\
                outerjoin(A_Key, A_Tag.fk_key == A_Key.id).\
                outerjoin(A_Value, A_Tag.fk_value == A_Value.id).\
                filter(A_Key.key.in_(original_attributes))

            if translate is True:
                key_translation, value_translation = self.\
                    get_translation_queries('a')
                query = query.add_columns(
                    key_translation.c.key_translated.label('key_translated'),
                    value_translation.c.value_translated.label(
                        'value_translated')
                ).\
                    outerjoin(
                        key_translation,
                        key_translation.c.key_original_id == A_Key.id).\
                    outerjoin(
                        value_translation,
                        value_translation.c.value_original_id == A_Value.id)
            else:
                query = query.add_columns(
                    A_Key.key.label('key_translated'),
                    A_Value.value.label('value_translated'))

            if taggroup_geometry is True:
                query = query.\
                    add_columns(A_Tag_Group.geometry).\
                    filter(A_Tag_Group.geometry != None)

        return query

    def query_to_features(
            self, query, involvements='none', public_query=False,
            with_taggroup_geometry=False, translate=True):
        """
        Transform the query to features. Every value of each
        :term:`Activity` is a line of the query. These attributes have
        to be collected to form an ActivityFeature. Also add involvement
        to the features.

        Args:
            ``query`` (sqlalchemy.orm.query.Query): A SQLAlchemy Query
            for the :term:`Activities`.

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

            ``with_taggroup_geometry`` (bool): An optional boolean
            indicating whether to add Taggroup geometries or not.
            Defaults to ``False``.

            ``translate`` (bool): An optional boolean indicating whether
            to return translated values or not. Defaults to ``True``.

        Returns:
            ``list``. A list of
            :class:`lmkp.protocols.features.ItemFeature`.
        """
        logged_in, is_moderator = get_user_privileges(self.request)

        if with_taggroup_geometry is True:
            query = query.add_columns(
                A_Tag_Group.geometry.label('tg_geometry')
            )

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

            # Use UID and version to find existing ActivityFeature or create a
            # new one
            feature = None
            for f in features:
                if (f.identifier == identifier and f.version == q.version
                        and f.order_value == q.order_value):
                    feature = f

            if feature is None:
                feature = ActivityFeature(
                    q.id, identifier, q.order_value, q.version, q.status_id,
                    q.geometry)

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
                taggroup = ActivityTaggroup(taggroup_id, q.tg_id, q.main_tag)
                # Set the taggroup geometry if available
                if with_taggroup_geometry is True:
                    taggroup.geometry = getattr(q, 'tg_geometry', None)
                feature.add_taggroup(taggroup)

            # Because of Involvements, the same Tags appears for each
            # Involvement, so add it only once to TagGroup
            if taggroup is not None and taggroup.get_tag_by_id(q.tag) is None:
                taggroup.add_tag(ItemTag(q.tag, key, value))

            # Involvements
            if involvements != 'none' and q.stakeholder_identifier is not None:

                involvement = InvolvementFeature(
                    q.stakeholder_identifier, q.stakeholder_version,
                    q.stakeholder_status, q.stakeholder_role,
                    q.stakeholder_role_id, q.stakeholder_username)

                feature.add_or_replace_involvement(
                    involvement, self.request, public_query=public_query)

        if involvements == 'full':
            """
            If full involvements are to be shown, collect the
            identifiers and versions of each Stakeholder as dict and
            prepare a list. Query the details (Taggroups) of these
            Stakeholders using the StakeholderProtocol and replace the
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
            from lmkp.protocols.stakeholder_protocol import StakeholderProtocol
            sp = StakeholderProtocol(self.request)
            relevant_query = sp.get_relevant_query_from_list(involvement_dicts)
            sh_query = sp.query_many(
                relevant_query, with_involvements=False, return_count=False)
            sh_features = sp.query_to_features(sh_query, involvements='none')

            # TODO: There might be some improvements possible here
            for a_feature in features:
                for sh_feature in sh_features:
                    inv = a_feature.get_involvement_by_identifier_version(
                        sh_feature.identifier, sh_feature.version)
                    if inv is not None:
                        inv.feature = sh_feature

        return features

    def query_to_geojson(self, query):
        """
        Transform the query to features, respectively their GeoJSON
        representation.

        Args:
            ``query`` (sqlalchemy.orm.query.Query): A SQLAlchemy Query
            for the :term:`Activities`.

        Returns:
            ``dict``. A GeoJSON compatible representation of the
            :term:`Activity` features.
        """
        features = []
        for q in query.all():
            key = None
            value = None
            try:
                key = q.key
                if q.key_translated is not None:
                    key = q.key_translated
                value = q.value
                if q.value_translated is not None:
                    value = q.value_translated
            except AttributeError:
                pass

            # Use UID and version to find existing ActivityFeature or create a
            # new one
            feature = None
            identifier = str(q.identifier)
            for f in features:
                if f.identifier == identifier and f.version == q.version:
                    feature = f

            if feature is None:
                feature = ActivityFeature(
                    q.id, identifier, None, q.version, q.status_id, q.geometry)
                features.append(feature)

            if key is not None and value is not None:
                try:
                    value = float(value)
                except ValueError:
                    pass
                feature.set_geojson_property(key, value)

        return {
            'type': 'FeatureCollection',
            'features': [f.to_geojson(self.request) for f in features]
        }

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
