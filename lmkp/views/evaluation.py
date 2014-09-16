from datetime import timedelta
from lmkp.models.database_objects import *
from lmkp.views.views import BaseView
from lmkp.views.views import get_current_profile
from lmkp.models.meta import DBSession as Session
from pyramid.view import view_config
from pyramid.view import view_defaults
from sqlalchemy import distinct
from sqlalchemy import func
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import Float
from geoalchemy.functions import functions

#@view_defaults(request_method='GET')
class EvaluationView(BaseView):

    @view_config(route_name='charts', renderer='lmkp:templates/ext_charts.mak')
    def show_charts(self):

        self._handle_parameters()

        return {}

    @view_config(route_name='evaluation_json', renderer='json')
    def evaluation_json(self):
        request = self.request
        ret = {'success': False}

        # temp
        tempSwitch = request.matchdict.get('temp', None)
        if tempSwitch == '1':
            groupby = request.params.get('groupby', 'Intention of Investment')

            input = {
            'item': 'Activity',
                'filter': {
                    'geometry': '',
                    'sql': ''
                },
                'attributes': {
                    'Activity': 'count',
                    'Intended area (ha)': 'sum'
                },
                'group_by': [groupby]
            }
        elif tempSwitch == '2':
            input = {
            'item': 'Activity',
                'filter': {
                    'geometry': '',
                    'sql': ''
                },
                'attributes': {
                    'Activity': 'count',
                    'Name of Investor': 'count distinct'
                },
                'group_by': ['Country']
            }
        elif tempSwitch == '3':
            input = {
            'item': 'Activity',
                'filter': {
                    'geometry': '',
                    'sql': ''
                },
                'attributes': {
                    'Contract area (ha)': 'sum',
                    'Activity': 'count'
                },
                'group_by': ['Country', 'Country of Investor']
            }
        elif tempSwitch == '4':
            input = {
            'item': 'Activity',
                'filter': {
                    'geometry': '',
                    'sql': ''
                },
                'attributes': {
                    'Activity': 'count',
                    'Contract area (ha)': 'sum'
                },
                'group_by': ['Year of agreement']
            }
        elif tempSwitch == '5':
            input = {
                    'item': 'Activity',
                    'filter': {
                        'geometry': '',
                        'sql': ''
                    },
                    'attributes': {
                        'Activity': 'count',
                        'Contract area (ha)': 'sum'
                    },
                    'group_by': ['Year of agreement', 'Intention of Investment']
                }
        elif tempSwitch == '6':
            input = {
                'item': 'Stakeholder',
                'filter': {
                    'geometry': '',
                    'sql': ''
                },
                'attributes': {
                    'Stakeholder': 'count'
                },
                'group_by': ['Country']
            }
        else:
            ret['msg'] = 'Temporarily only /1, /2 and /3 available.'
            return ret


        if input['item'] == 'Stakeholder':
            Item = Stakeholder
            Tag_Group = SH_Tag_Group
            Tag = SH_Tag
            Key = SH_Key
            Value = SH_Value
        else:
            Item = Activity
            Tag_Group = A_Tag_Group
            Tag = A_Tag
            Key = A_Key
            Value = A_Value

        # Test input
        if 'group_by' not in input:
            ret['msg'] = "Missing parameter 'group by': At least one column needs to be specified."
            return ret
        if not isinstance(input['group_by'], list):
            ret['msg'] = "Parameter 'group by' needs to be an array."
            return ret
        if 'attributes' not in input:
            ret['msg'] = "Missing attributes: No attributes were specified."
            return ret
        for attr in input['attributes']:
            test = self._checkFunction(Item, Tag_Group, Tag, Key, Value, input['attributes'][attr], attr)
            if test is not True:
                ret['msg'] = test
                return ret

        # Get groups
        groups_subqueries, groups_columns = self._getGroupBy(Item, Tag_Group, Tag, Key, Value, input['group_by'])

        # Get functions
        functions_subqueries, functions_columns = self._getAttributeFunctions(Item, Tag_Group, Tag, Key, Value, input['attributes'])

        # Prepare basic query (already joins first group)
        q = Session.query(*groups_columns + functions_columns).\
            join(Tag_Group).\
            join(Item)

        # Join with further groups
        for g_sq in groups_subqueries[1:]:
            q = q.outerjoin(g_sq, g_sq.c.a_id == Item.id)

        # Join with functions
        for f_sq in functions_subqueries:
            q = q.outerjoin(f_sq, f_sq.c.a_id == Item.id)

        # Apply status filter (fix: active)
        fk_status = Session.query(Status.id).filter(Status.name == 'active')
        q = q.filter(Item.fk_status == fk_status)

        # Apply profile boundary filter
        if Item == Activity:
            profile = Session.query(Profile).\
                filter(Profile.code == get_current_profile(request)).\
                first()
            if profile is not None:
                q = q.filter(functions.intersects(Item.point, profile.geometry))

        # Apply grouping and ordering
        q = q.group_by(*groups_columns).\
            order_by(groups_columns[0])

        data = []
        for res in q.all():
            entry = {}
            # first go through group_by
            for i, group in enumerate(input['group_by']):
                entry[group] = res[i]
            # then go through functions
            for i, attr in enumerate(input['attributes']):
                displayAttr = attr
                if attr == 'Activity':
                    displayAttr = 'Deals'
                entry["%s (%s)" % (displayAttr, input['attributes'][attr])] = res[i + len(input['group_by'])]
            data.append(entry)

        ret['success'] = True
        ret['data'] = data

        return ret

    def _getAttributeFunctions(self, Item, Tag_Group, Tag, Key, Value, attributes):
        """
        Returns
        - an array with SubQueries
        - an array with Columns to select from
        """
        subqueries = []
        columns = []
        for attr in attributes:
            function = attributes[attr]
            if function == 'sum':
                sq = Session.query(Item.id.label('a_id'),
                                   cast(Value.value, Float).label('v')).\
                    join(Tag_Group).\
                    join(Tag, Tag_Group.id == Tag.fk_tag_group).\
                    join(Value, Value.id == Tag.fk_value).\
                    join(Key, Key.id == Tag.fk_key).\
                    filter(Key.key == attr).\
                    subquery()
                subqueries.append(sq)
                columns.append(func.sum(sq.c.v))
            elif function == 'count' or function == 'count distinct':
                if attr == 'Activity' or attr == 'Stakeholder':
                    columns.append(func.count())
                else:
                    sq = Session.query(Item.id.label('a_id'),
                                       Value.value.label('v')).\
                        join(Tag_Group).\
                        join(Tag, Tag_Group.id == Tag.fk_tag_group).\
                        join(Value).\
                        join(Key).\
                        filter(Key.key == attr).\
                        subquery()
                    subqueries.append(sq)
                    if (function == 'count distinct'):
                        columns.append(func.count(distinct(sq.c.v)))
                    else:
                        columns.append(func.count(sq.c.v))
        return subqueries, columns

    def _checkFunction(self, Item, Tag_Group, Tag, Key, Value, function, attr):
        """
        Returns True if a function is predefined and if targeted
        attribute is of valid type (where needed)
        """
        if function == 'sum':
            if self._castToNumber(Item, Tag_Group, Tag, Key, Value, attr):
                return True
            else:
                return "Invalid type for function '%s': '%s' should contain only number values." % (function, attr)
        if function == 'count':
            return True
        if function == 'count distinct':
            return True
        else:
            return "Unknown function: '%s' is not a predefined function." % function

    def _getGroupBy(self, Item, Tag_Group, Tag, Key, Value, group_by):
        """
        Returns
        - an array with SubQueries
        - an array with Columns to select from
        """
        subqueries = []
        columns = []
        for i, gb in enumerate(group_by):
            # first one different
            if i == 0:
                sq = Session.query(Value.value.label('v'),
                                   Tag.fk_tag_group.label('group1_taggroupid')).\
                    join(Tag).\
                    join(Key).\
                    filter(Key.key == gb).\
                    subquery()
            else:
                sq = Session.query(Item.id.label('a_id'),
                                   Value.value.label('v')).\
                    join(Tag_Group).\
                    join(Tag, Tag_Group.id == Tag.fk_tag_group).\
                    join(Value).\
                    join(Key).\
                    filter(Key.key == gb).\
                    subquery()
            subqueries.append(sq)
            columns.append(sq.c.v)
        return subqueries, columns

    def _castToNumber(self, Item, Tag_Group, Tag, Key, Value, key):
        """
        Returns True if the given key has number values
        """
        q = Session.query(cast(A_Value.value, Float)).\
            join(A_Tag).\
            join(A_Key).\
            filter(A_Key.key == key)
        try:
            x = q.all()
            return True
        except:
            return False
