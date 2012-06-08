from pyramid.view import view_config
from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession as Session

from sqlalchemy import func
from sqlalchemy import distinct
from sqlalchemy.types import Float
from sqlalchemy.sql.expression import cast



@view_config(route_name='evaluation_json', renderer='json')
def evaluation_json(request):
    ret = {'success': False}
    
    # temp
    tempSwitch = request.matchdict.get('temp', None)
    if tempSwitch == '1':
        input = {
                'filter': {
                    'geometry': '',
                    'sql': ''
                },
                'attributes': {
                    'Activity': 'count'
                },
                'group_by': ['Main Crop']
            }
    elif tempSwitch == '2':
        input = {
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
                'filter': {
                    'geometry': '',
                    'sql': ''
                },
                'attributes': {
                    'Size of Investement': 'sum',
                    'Activity': 'count'
                },
                'group_by': ['Country', 'Country of Investor']
            }
    else:
        ret['msg'] = 'Temporarily only /1, /2 and /3 available.'
        return ret
    
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
        test = _checkFunction(input['attributes'][attr], attr)
        if test is not True:
            ret['msg'] = test
            return ret
    
    # Get groups
    groups_subqueries, groups_columns = _getGroupBy(input['group_by'])

    # Get functions
    functions_subqueries, functions_columns = _getAttributeFunctions(input['attributes'])

    # Prepare basic query (already joins first group)
    q = Session.query(*groups_columns + functions_columns).\
        join(A_Tag_Group).\
        join(Activity)

    # Join with further groups
    for g_sq in groups_subqueries[1:]:
        q = q.outerjoin(g_sq, g_sq.c.a_id == Activity.id)

    # Join with functions
    for f_sq in functions_subqueries:
        q = q.outerjoin(f_sq, f_sq.c.a_id == Activity.id)
    
    # Apply status filter (fix: active)
    fk_status = Session.query(Status.id).filter(Status.name == 'active')
    q = q.filter(Activity.fk_status == fk_status)
    
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
            entry["%s (%s)" % (attr, input['attributes'][attr])] = res[i+len(input['group_by'])]
        data.append(entry)
    
    ret['success'] = True
    ret['data'] = data
    
    return ret

def _getAttributeFunctions(attributes):
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
            sq = Session.query(Activity.id.label('a_id'),
                               cast(A_Value.value, Float).label('v')).\
                 join(A_Tag_Group).\
                 join(A_Tag, A_Tag_Group.id == A_Tag.fk_a_tag_group).\
                 join(A_Value).\
                 join(A_Key).\
                 filter(A_Key.key == attr).\
                 subquery()
            subqueries.append(sq)
            columns.append(func.sum(sq.c.v))
        elif function == 'count' or function == 'count distinct':
            if attr == 'Activity':
                columns.append(func.count())
            else:
                sq = Session.query(Activity.id.label('a_id'),
                                   A_Value.value.label('v')).\
                     join(A_Tag_Group).\
                     join(A_Tag, A_Tag_Group.id == A_Tag.fk_a_tag_group).\
                     join(A_Value).\
                     join(A_Key).\
                     filter(A_Key.key == attr).\
                     subquery()
                subqueries.append(sq)
                if (function == 'count distinct'):
                    columns.append(func.count(distinct(sq.c.v)))
                else:
                    columns.append(func.count(sq.c.v))
    return subqueries, columns

def _checkFunction(function, attr):
    """
    Returns True if a function is predefined and if targeted 
    attribute is of valid type (where needed)
    """
    if function == 'sum':
        if _castToNumber(attr):
            return True
        else:
            return "Invalid type for function '%s': '%s' should contain only number values." % (function, attr)
    if function == 'count':
        return True
    if function == 'count distinct':
        return True
    else:
        return "Unknown function: '%s' is not a predefined function." % function

def _getGroupBy(group_by):
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
            sq = Session.query(A_Value.value.label('v'),
                               A_Tag.fk_a_tag_group.label('group1_taggroupid')).\
                       join(A_Tag).\
                       join(A_Key).\
                       filter(A_Key.key == gb).\
                       subquery()
        else:
            sq = Session.query(Activity.id.label('a_id'),
                               A_Value.value.label('v')).\
                       join(A_Tag_Group).\
                       join(A_Tag, A_Tag_Group.id == A_Tag.fk_a_tag_group).\
                       join(A_Value).\
                       join(A_Key).\
                       filter(A_Key.key == gb).\
                       subquery()
        subqueries.append(sq)
        columns.append(sq.c.v)
    return subqueries, columns

def _castToNumber(key):
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
