from pyramid.i18n import (
    TranslationStringFactory,
    get_localizer,
)
from sqlalchemy import (
    func,
)
from sqlalchemy.sql.expression import (
    and_,
    between,
    cast,
    or_,
)
from sqlalchemy.types import Float

from lmkp.authentication import get_user_privileges
from lmkp.models.database_objects import (
    A_Key,
    A_Tag,
    A_Tag_Group,
    A_Value,
    Activity,
    Changeset,
    Language,
    SH_Key,
    SH_Tag,
    SH_Tag_Group,
    SH_Value,
    Stakeholder,
)
from lmkp.models.meta import DBSession as Session
from lmkp.utils import validate_item_type
from lmkp.views.views import (
    get_status_parameter,
    get_current_locale,
    get_current_attribute_filters,
    get_current_order_key,
)

_ = TranslationStringFactory('lmkp')

# TODO: hard-coded status list
STATUS_ARRAY = [
    (1, 'pending', _('pending')),
    (2, 'active', _('active')),
    (3, 'inactive', _('inactive')),
    (4, 'deleted', _('deleted')),
    (5, 'rejected', _('rejected')),
    (6, 'edited', _('edited'))
]


def get_status_ids():
    """
    Return every status ID known.

    Returns:
        ``list``. A list with all status IDs available.
    """
    return [s[0] for s in STATUS_ARRAY]


def get_status_id_by_code(code):
    """
    Return a status ID based on its internal code.

    Args:
        ``code`` (str): The internal code (eg. ``pending``, ``active``
        of the status.

    Returns:
        ``int`` or ``None``. The ID of the status or None if the status
        was not found.
    """
    for s in STATUS_ARRAY:
        if s[1] == code:
            return s[0]
    return None


def get_status_name_by_id(id, request=None):
    """
    Return the name of a status based on its ID. If ``request`` is
    provided, the translated name is returned.

    Args:
        ``id`` (int): The ID of the status.

        ``request`` (pyramid.request): The optional :term:`Pyramid`
        Request object. If it is provided, the status name is returned
        translated.

    Returns:
        ``str`` or ``None``. The (eventually translated) name of the
        status or None if the status was not found.
    """
    for s in STATUS_ARRAY:
        if s[0] == id:
            if request is None:
                return s[2]
            else:
                localizer = get_localizer(request)
                return localizer.translate(s[2])
    return None


class Protocol(object):
    """
    The Protocol handles all query and create operations with
    :term:`Activities` and :term:`Stakeholders`.

    .. seealso::
       :class:`lmkp.protocols.activity_protocol.ActivityProtocol` and
       :class:`lmkp.protocols.stakeholder_protocol.StakeholderProtocol`
    """

    def __init__(self, request):
        self.request = request
        self.Session = Session

    def get_valid_status_ids(self, context, logged_in, is_moderator):
        """
        Return the :term:`status` IDs which are valid within a given
        context.

        Args:
            ``context`` (str): The context of the query. Possible values
            are:

                * ``filter``: Which statuses are valid as status filter
                  when querying many :term:`Items`. Pending or edited
                  versions are only visible to moderators.

                * ``involvements``: Which statuses are valid on the
                  other side of :term:`involvements`. By default, these
                  are active and inactive versions. For logged in users,
                  also pending and edited.

                * ``history``: Which statuses are valid when viewing the
                  history of a single :term:`Item`. By default, these
                  are only active and inactive versions. For moderators,
                  all other statuses are also valid (geographical filter
                  needs to be applied manually)

            ``logged_in`` (bool): A boolean indicating whether a user is
            logged in or not.

            ``is_moderator`` (bool): A boolean indicating whether a user
            is moderator within the current profile or not.

        Returns:
            ``list``. A list with :term:`status` IDs which are valid
            within the given context.
        """
        status_ids = get_status_ids()
        if context == 'filter':
            if not is_moderator:
                status_ids.remove(1)
                status_ids.remove(6)

        elif context == 'involvements':
            status_ids.remove(4)
            status_ids.remove(5)
            if not logged_in:
                status_ids.remove(1)
                status_ids.remove(6)

        elif context == 'history':
            if not logged_in or not is_moderator:
                status_ids.remove(1)
                status_ids.remove(4)
                status_ids.remove(5)
                status_ids.remove(6)

        else:
            raise Exception('Unknown context: %s' % context)

        return status_ids

    def get_attribute_filters(self):
        """
        Return two lists of SQLAlchemy queries containing the filters
        for attributes of :term:`Activities` and :term:`Stakeholders`
        respectively.

        Request parameters:
            ``[filter_expression]`` (str): One or more filter expression
            for :term:`Activities` or :term:`Stakeholders`.

            .. seealso::
               :class:`lmkp.views.views.get_current_attribute_filters`

        Returns:
            ``list``. A list of SQLAlchemy queries joining the
            :term:`Activity` taggroups with their tags and keys to
            provide a filter based on the given attributes.

            ``list``. A list of SQLAlchemy queries joining the
            :term:`Stakeholder` taggroups with their tags and keys to
            provide a filter based on the given attributes.
        """
        def _get_filter_expression(prefix, value, op):

            # Use prefix to determine if A_Value or SH_Value
            if prefix == 'a':
                v = A_Value
            elif prefix == 'sh':
                v = SH_Value
            else:
                return None

            # Use cast function provided by SQLAlchemy to convert
            # database values to Float.
            # Note: PostgreSQL throws a cast error if comparison operator
            # 'equal' (=) is used. Therefore, 'between' is used.
            nbr_map = {
                'eq': between(cast(v.value, Float), value, value),
                'ne': cast(v.value, Float) != value,
                'lt': cast(v.value, Float) < value,
                'lte': cast(v.value, Float) <= value,
                'gt': cast(v.value, Float) > value,
                'gte': cast(v.value, Float) >= value
            }

            str_map = {
                # Operators like ~ or ~* do not seem to work correctly so we
                # are using LIKE and NOT LIKE instead. Also replace "*" with
                # the Postgresql wildcard character "%"
                'like': v.value.op("LIKE")(value.replace('*', "%")),
                'ilike': v.value.op("ILIKE")(value.replace('*', "%")),
                'nlike': v.value.op("NOT LIKE")(value.replace('*', "%")),
                'nilike': v.value.op("NOT ILIKE")(value.replace('*', "%"))
            }

            # number comparison
            if op in nbr_map.keys():
                # make sure submitted value is a number
                try:
                    float(value)
                    return nbr_map[op]
                except:
                    pass

            elif op in str_map.keys():
                return str_map[op]

            return None

        a_filters = []
        sh_filters = []
        for prefix, col, op, values in get_current_attribute_filters(
                self.request):
            if prefix == 'a':
                for v in values.split(','):
                    q = self.Session.query(
                        A_Tag.fk_a_tag_group.label('a_filter_tg_id')
                    ).\
                        join(A_Key, A_Key.id == A_Tag.fk_key).\
                        join(A_Value, A_Value.id == A_Tag.fk_value).\
                        filter(A_Key.key == col).\
                        filter(A_Key.fk_language == None).\
                        filter(_get_filter_expression(prefix, v, op))
                    a_filters.append(q)
            elif prefix == 'sh':
                for v in values.split(','):
                    q = self.Session.query(
                        SH_Tag.fk_sh_tag_group.label('sh_filter_tg_id')
                    ).\
                        join(SH_Key, SH_Key.id == SH_Tag.fk_key).\
                        join(SH_Value, SH_Value.id == SH_Tag.fk_value).\
                        filter(SH_Key.key == col).\
                        filter(SH_Key.fk_language == None).\
                        filter(_get_filter_expression(prefix, v, op))
                    sh_filters.append(q)

        return a_filters, sh_filters

    def get_order(self, item_type):
        """
        Returns a SQLAlchemy subquery with the :term:`Item` id and the
        value to order by. If all values are numeric, they are casted
        to floating point numbers.

        Request parameters:
            ``order_by`` (str): The key to order by.

            .. seealso::
               :class:`lmkp.views.views.get_current_order_key`

        Args:
            ``item_type`` (str): The :term:`Item Type` of the
            :term:`Item`.

        Returns:
            ``sqlalchemy.sql.expression``. A SQLAlchemy subquery.
        """
        if validate_item_type(item_type) == 'a':
            Item = Activity
            Taggroup = A_Tag_Group
            Tag = A_Tag
            Key = A_Key
            Value = A_Value
        else:
            Item = Stakeholder
            Taggroup = SH_Tag_Group
            Tag = SH_Tag
            Key = SH_Key
            Value = SH_Value

        order_key = get_current_order_key(self.request)
        if order_key == 'timestamp':
            order_query = self.Session.query(
                Item.id,
                Changeset.timestamp.label('value')
            ).\
                join(Changeset).\
                subquery()
            return order_query

        else:
            order_query = self.Session.query(
                Item.id,
            ).\
                join(Taggroup).\
                join(Tag, Tag.fk_tag_group == Taggroup.id).\
                join(Value, Value.id == Tag.fk_value).\
                join(Key, Key.id == Tag.fk_key).\
                filter(Key.key.like(order_key))

            order_query_strings = order_query.add_column(
                Value.value.label('value'))

            for v in order_query_strings.all():
                try:
                    float(v.value)
                except ValueError:
                    return order_query_strings.subquery()

            order_query_numbers = order_query.add_column(
                cast(Value.value, Float).label('value'))
            return order_query_numbers.subquery()

    def get_translation_queries(self, item_type):
        """
        Returns two SQLAlchemy subqueries with the translations for the
        keys and values of the :term:`Item`.

        Args:
            ``item_type`` (str): The :term:`Item Type` of the
            :term:`Item`.

        Returns:
            ``sqlalchemy.sql.expression``. A SQLAlchemy subquery for the
            keys of the :term:`Item`.

            ``sqlalchemy.sql.expression``. A SQLAlchemy subquery for the
            values of the :term:`Item`.
        """
        if validate_item_type(item_type) == 'a':
            Key = A_Key
            Value = A_Value
        else:
            Key = SH_Key
            Value = SH_Value
        current_locale = get_current_locale(self.request)
        key_query = self.Session.query(
            Key.fk_key.label("key_original_id"),
            Key.key.label("key_translated")
        ).\
            join(Language).\
            filter(Language.locale == current_locale).\
            subquery()
        value_query = self.Session.query(
            Value.fk_value.label("value_original_id"),
            Value.value.label("value_translated")
        ).\
            join(Language).\
            filter(Language.locale == current_locale).\
            subquery()
        return key_query, value_query

    def apply_visible_version_filter(
            self, item_type, query, public_query=False):
        """
        Apply a filter to a query in order to limit the versions of an
        :term:`Item` that are visible. Unlike
        :func:`apply_many_visible_version_filter`, this function always
        returns only a single version per :term:`Item`.

        The filter is based on the :term:`status` of the :term:`Item`
        and the following rules apply:

        * **Status filter first**: If a status filter is set and valid,
          it is considered first (eg. status filter set to ``active``
          will not return pending versions, even for moderators).

          .. seealso::
               :func:`lmkp.protocols.protocol.Protocol.get_valid_status_ids`
               with ``context=filter``.

        * **Public** (not logged in or ``public_query=True``): By
          default, only active versions are visible. Status filters can
          be applied within the statuses visible to the public (eg. no
          pending or rejected versions).

        * **Logged in**: By default, users can see their own pending
          versions if they are newer than the active version. Status
          filters can be applied, also on pending or rejected versions.

        * **Moderators**: By default, :term:`moderators` can see pending
          versions within their profile if they are newer than the
          active version. Status filters can be applied, also on pending
          or rejected versions.

        Args:
            ``item_type`` (str): The :term:`Item Type` of the
            :term:`Item`.

            ``query`` (sqlalchemy.orm.query.Query): A SQLAlchemy Query
            object on either :term:`Activities` or :term:`Stakeholders`.

            ``public_query`` (bool): An optional boolean indicating
            whether to return only versions visible to the public (eg.
            no pending) or not.

        Returns:
            ``sqlalchemy.orm.query.Query``. The filtered SQLAlchemy
            Query.
        """
        if validate_item_type(item_type) == 'a':
            Item = Activity
        else:
            Item = Stakeholder

        logged_in, is_moderator = get_user_privileges(self.request)

        status_filter_param = get_status_parameter(self.request)
        status_filter_array = []
        if status_filter_param is not None:
            valid_status_ids = self.get_valid_status_ids(
                'filter', logged_in, is_moderator)
            for s in status_filter_param.split(','):
                status_id = get_status_id_by_code(s)
                if status_id is None:
                    continue
                if status_id not in valid_status_ids:
                    continue
                status_filter_array.append(status_id)

        show_pending_in_results = (
            len(status_filter_array) == 0 or 1 in status_filter_array)

        if show_pending_in_results and logged_in and public_query is False:
            visible_version_filters = []

            if len(status_filter_array) == 0 or 2 in status_filter_array:
                visible_version_filters.append(Item.fk_status == 2)

            visible_version_filters.append(
                and_(
                    Item.fk_status == 1,
                    Changeset.fk_user == self.request.user.id
                )
            )
            if is_moderator:
                if item_type == 'a':
                    visible_version_filters.append(
                        and_(
                            Item.fk_status == 1,
                            self.get_user_spatial_profile_filter()
                        )
                    )
                else:
                    visible_version_filters.append(Item.fk_status == 1)

            latest_visible_version = self.Session.query(
                Item.identifier.label('identifier'),
                func.max(Item.version).label('max_version')
            ).\
                join(Changeset).\
                filter(or_(* visible_version_filters)).\
                group_by(Item.identifier).\
                subquery()

            query = query.\
                join(latest_visible_version, and_(
                    latest_visible_version.c.identifier == Item.identifier,
                    latest_visible_version.c.max_version == Item.version
                ))

        elif len(status_filter_array) > 0:
            query = query.filter(Item.fk_status.in_(status_filter_array))

        else:
            query = query.filter(Item.fk_status == 2)

        return query

    def apply_many_visible_version_filter(
            self, item_type, query, public_query=False):
        """
        Apply a filter to a query in order to limit the versions of
        multiple :term:`Items` (or versions of them) that are visible.
        Unlike :func:`apply_visible_version_filter`, this function
        returns multiple versions for the same :term:`Item` and not only
        a single one.

        The filter is based on the :term:`status` of the versions and
        the following rules apply:

        * **Status**: Visible statuses are filtered based on the
          function ``get_valid_status_ids``.

          .. seealso::
               :func:`lmkp.protocols.protocol.Protocol.get_valid_status_ids`
               with ``context=history``.

        * **Public** (not logged in or ``public_query=True``): Only
          active and inactive versions are visible.

        * **Logged in**: Users can see all of their own versions,
          regardless of their status.

        * **Moderators**: :term:`Moderators` can see all versions within
          their profile, regardless of their status.

        Args:
            ``item_type`` (str): The :term:`Item Type` of the
            :term:`Item`.

            ``query`` (sqlalchemy.orm.query.Query): A SQLAlchemy Query
            object on either :term:`Activities` or :term:`Stakeholders`.

            ``public_query`` (bool): An optional boolean indicating
            whether to return only versions visible to the public or
            not.

        Returns:
            ``sqlalchemy.orm.query.Query``. The filtered SQLAlchemy
            Query.
        """
        if validate_item_type(item_type) == 'a':
            Item = Activity
        else:
            Item = Stakeholder

        if public_query is True:
            logged_in, is_moderator = False, False
        else:
            logged_in, is_moderator = get_user_privileges(self.request)

        filters = [
            Item.fk_status.in_(
                self.get_valid_status_ids('history', False, False))
        ]

        if logged_in is True:
            filters.append(Changeset.fk_user == self.request.user.id)

            if is_moderator is True:
                if item_type == 'a':
                    filters.append(
                        and_(
                            Item.fk_status.in_(
                                self.get_valid_status_ids(
                                    'history', logged_in, is_moderator)),
                            self.get_user_spatial_profile_filter()
                        )
                    )
                else:
                    filters.append(Item.fk_status.in_(
                        self.get_valid_status_ids(
                            'history', logged_in, is_moderator)))

        visible_versions = self.Session.query(
            Item.identifier.label('identifier'),
            Item.version.label('version')
        ).\
            join(Changeset).\
            filter(or_(* filters)).\
            subquery()

        query = query.\
            join(visible_versions, and_(
                visible_versions.c.identifier == Item.identifier,
                visible_versions.c.version == Item.version
            ))
        return query

    def _get_user_status(self, principals=None):
        # TODO: Remove

        if principals is not None:
            return (
                'system.Authenticated' in principals,
                'group:moderators' in principals
            )

        return (
            None,
            None
        )
