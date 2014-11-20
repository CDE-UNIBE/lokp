import collections
import datetime
import geojson
import json
import logging

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.i18n import get_localizer
from pyramid.renderers import render
from pyramid.security import (
    effective_principals,
    unauthenticated_userid,
)
from shapely import wkb
from shapely.geometry import mapping as asGeoJSON
from shapely.geometry import asShape
from sqlalchemy.sql.expression import (
    cast,
    and_,
    between,
)
from sqlalchemy.types import Float
from sqlalchemy import func

from lmkp.custom import get_customized_template_path
from lmkp.models.database_objects import (
    A_Key,
    A_Tag,
    A_Tag_Group,
    A_Value,
    Activity,
    Changeset,
    Group,
    Involvement,
    Language,
    Permission,
    SH_Key,
    SH_Tag,
    SH_Tag_Group,
    SH_Value,
    Stakeholder,
    Stakeholder_Role,
    Status,
    User,
)
from lmkp.views.files import check_file_location_name
from lmkp.views.form_config import getCategoryList
from lmkp.views.review import BaseReview
from lmkp.views.translation import statusMap
from lmkp.views.translation import get_translated_status
from lmkp.authentication import get_user_privileges
from lmkp.views.views import get_status_parameter
from lmkp.views.views import get_current_attribute_filters
from lmkp.views.views import get_current_order_key
from lmkp.models.meta import DBSession as Session
from lmkp.utils import validate_item_type

# TODO: hard-coded status list
STATUS_ARRAY = [
    'pending',
    'active',
    'inactive',
    'deleted',
    'rejected',
    'edited'
]


class Protocol(object):

    def __init__(self, request):
        self.request = request
        self.Session = Session

    def get_status_filter(self, db_object):
        """
        Return an SQLAlchemy filter expression based on the status
        parameter of the request.

        Pending or edited versions can only be seen by moderators and
        are not returned otherwise.

        Args:
            ``db_object`` (Model): A SQLAlchemy database model, either
            :term:`Activity` or :term:`Stakeholder`.

        Request parameters:
             ``status`` (str): A comma-separated list of status names.

        Returns:
            ``sqlalchemy.sql.expression``. An SQLAlchemy expression
            corresponding to ``db_object.fk_status in [1,2] which can be
            used as a filter on the ``db_object``.

            An example of the SQL equivalent of the expression could be:
            ``data.activities.fk_status IN (1, 2)``
        """
        status_param = get_status_parameter(self.request)
        logged_in, is_moderator = get_user_privileges(self.request)
        status_array = []
        if status_param is not None:
            for s in status_param.split(','):
                try:
                    status_id = STATUS_ARRAY.index(s) + 1
                except ValueError:
                    continue
                if status_id in [1, 6] and not is_moderator:
                    continue
                status_array.append(status_id)
        if len(status_array) == 0:
            status_array = [2]
        return db_object.fk_status.in_(status_array)

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

    def _get_limit(self, request):

        limit = request.params.get('limit', None)
        if limit is not None:
            try:
                return int(limit)
            except ValueError:
                pass

        return None

    def _get_offset(self, request):
        """
        Returns the requested offset, default value is 0
        """
        offset = request.params.get('offset', 0)
        try:
            return int(offset)
        except ValueError:
            pass

        return 0

    def _get_translatedKV(self, lang, Key, Value):
        """
        Returns
        - a SubQuery with a list of all translated keys
        - a SubQuery with a list of all translated values
        """
        key_query = self.Session.query(
            Key.fk_key.label("key_original_id"),
            Key.key.label("key_translated")
        ).\
            filter(Key.language == lang).\
            subquery()
        value_query = self.Session.query(
            Value.fk_value.label("value_original_id"),
            Value.value.label("value_translated")
        ).\
            filter(Value.language == lang).\
            subquery()
        return key_query, value_query

    def _get_involvement_status(self, request):
        """
        Returns a ClauseElement array of statuses used upon involvements.
        Default value is active.
        They are based on the following rules:
        - If not logged in, only show 'active' involvements
        """

        logged_in, is_moderator = self._get_user_status(
            effective_principals(request))

        statuses = [
            Status.name == 'active',
            Status.name == 'inactive'
        ]

        if logged_in:
            statuses.append(Status.name == 'pending')
            statuses.append(Status.name == 'edited')

        #log.debug("Involvement statuses [array]:\n%s" % statuses)

        return statuses

    def _get_user_status(self, principals=None):

        if principals is not None:
            return (
                'system.Authenticated' in principals,
                'group:moderators' in principals
            )

        return (
            None,
            None
        )
