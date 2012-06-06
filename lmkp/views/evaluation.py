from pyramid.view import view_config
from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession as Session

from sqlalchemy import func
from sqlalchemy.types import Float
from sqlalchemy.sql.expression import cast

@view_config(route_name='evaluation_json', renderer='json')
def evaluation_json(request):
    
    function = "sum"
    on_column = "Size of Investement"
    group = "Country"
    #group = "Main Crop"
    
    relevant_tags = Session.query(A_Tag.id.label('tag_id'),
                      A_Value.value.label('tag_value')).\
        join(A_Key).\
        join(A_Value).\
        filter(A_Key.key == on_column).\
        subquery()
    
    relevant_activities = Session.query(Activity.id.label('activity_id'),
                            cast(relevant_tags.c.tag_value, Float).label('tag_value')).\
        join(A_Tag_Group).\
        join(relevant_tags, relevant_tags.c.tag_id == A_Tag_Group.id).\
        subquery()
    
    query = Session.query(A_Value.value.label("group"),
                      func.sum(relevant_activities.c.tag_value).label("sum"),
                      func.count(relevant_activities.c.tag_value).label("count")).\
        join(A_Tag).\
        join(A_Tag_Group, A_Tag_Group.id == A_Tag.fk_a_tag_group).\
        join(relevant_activities, relevant_activities.c.activity_id == A_Tag_Group.fk_activity).\
        join(A_Key).\
        filter(A_Key.key == group).\
        group_by(A_Value.value).\
        all()
    
    
    data = []
    total_sum = 0
    total_count = 0
    for x in query:
        data.append({'group': x.group, 'sum': x.sum, 'count': x.count})
        total_sum += x.sum
        total_count += x.count
    
    return {'data': data, 'total_sum': total_sum, 'total_count': total_count}

