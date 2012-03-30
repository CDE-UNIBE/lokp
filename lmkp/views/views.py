from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession
from pyramid.security import authenticated_userid
from pyramid.view import view_config

#@view_config(route_name='home', renderer='../templates/mytemplate.pt')
def my_view(request):
# deleted from autocreated
#    one = DBSession.query(MyModel).filter(MyModel.name=='one').first()
#    return {'one':one, 'project':'MyProject'}
    return {'one':'one', 'project':'MyProject'}

@view_config(route_name='db_test', renderer='lmkp:templates/db_test.pt')
def db_test(request):

    from sqlalchemy import func, select
    #object = DBSession.query(View_Test).filter(View_Test.key == "name").all()
    #count = select([func.count(View_Test.value)]).group_by(View_Test.activity_id).alias()
    #object = DBSession.query(View_Test.activity_id, func.count('*')).group_by(View_Test.activity_id).group_by(View_Test.key).all()
    #keycount = DBSession.query(func.count(View_Test.key).label('keycount')).group_by(View_Test.activity_id).group_by(View_Test.key).subquery()
    #object = DBSession.query(keycount).filter(keycount.c.keycount > 1).all()
    from sqlalchemy import or_
    #object = DBSession.query(Activity).join(A_Changeset).filter(or_(A_Changeset.source.like('[active] Source %'), A_Changeset.source.like('[pending] Source %'))).all()
    #a = DBSession.query(Activity).join(A_Changeset).filter(A_Changeset.source.like('[overwritten] Source %')).filter(Activity.version==2).first()
    #object = a.tags
    session1 = DBSession()
    
    #t = session1.query(A_Value).get(114)
    
    #object = t.tags[0].tag_group.activity
    
    #object = request.params
    
    object = DBSession.query(A_Key).filter(A_Key.fk_a_key == None).all()
    
    
    # get old_activity
    #old_activity = session1.query(Activity).get(55)
   
    # set status of old_activity to "overwritten" (3)
    #old_activity.status = session1.query(Status).get(2)
   
#===============================================================================
# # instance of Activity needs to be created first
#    # create instance of Activity
#    new_activity = Activity(activity_identifier=old_activity.activity_identifier, version=3, point="POINT(11 22)")
#    new_activity.status = session1.query(Status).get(1) # pending
#   
# # instance of Tag_Group
#    # create instance of Tag_Group
#    new_tag_group = A_Tag_Group()
#   
# # instance of Tag
#    # prepare values for new Tag
#    new_key = session1.query(A_Key).first() 
#    new_value = A_Value(value="Testing")
#    language = session1.query(Language).first()
#    new_value.language = language
#   
#    # create instance of Tag
#    new_tag = A_Tag()
#    new_tag.key = new_key
#    new_tag.value = new_value
#   
#    #old_tag_value = old_activity.tag_groups[0].tags[0].value
#   
# # make connections (start off with A_Tag_Group)
#    new_tag_group.activity = new_activity # first attach Activity to Tag_Group
#    new_tag_group.tags.append(new_tag) # then attach Tags
#   
#    # copy old key/value pairs
#    for old_tag_group in old_activity.tag_groups:
#       copy_tag_group = A_Tag_Group()
#       for old_tag in old_tag_group.tags:
#           copy_tag = A_Tag()
#           copy_tag.fk_a_key = old_tag.fk_a_key
#           copy_tag.fk_a_value = old_tag.fk_a_value
#           copy_tag_group.tags.append(copy_tag)
#       new_activity.tag_groups.append(copy_tag_group)
#===============================================================================
   
# add to database (only add Activity, rest gets added as well)
    #session1.add(new_activity)
    
    
    #===========================================================================
    # import transaction
    # try:
    #    transaction.commit()
    #    message = "success!"
    # except AssertionError, msg:
    #    transaction.abort()
    #    message = msg
    #===========================================================================
        
    
    
    #t = session1.query(Activity).get(203)
    #a = session1.query(Activity).filter(Activity.activity_identifier == t.activity_identifier).all()
    
    
    #t = session1.query(View_Test).limit(5).first()
    
    #activities = session1.query(Activity)
    #active_activities = activities.filter(Activity.fk_status == 2)
    
    #object = active_activities.count()
    
    #===========================================================================
    # old_activity = session1.query(Activity).first()
    # lang = session1.query(Language).first()
    # status = session1.query(Status).first()
    # newKey = session1.query(A_Key).first()
    # newValue = A_Value(value='Test')
    # newValue.language = lang
    # newTag = A_Tag()
    # newTag.key = newKey
    # newTag.value = newValue
    # identifier = uuid.uuid4()
    # newActivity = Activity(activity_identifier=identifier, version=2, geometry="POINT(10 20)")
    # newActivity.status = status
    # newActivity.tags.append(newTag)
    # 
    # session1.add(newActivity)
    # import transaction
    # transaction.commit()
    #===========================================================================
    
    return {'object':object}

    activities = []
    for i in DBSession.query(Activity).join(A_Event).join(A_Tag).join(A_Key).filter(A_Key.key == 'Spatial uncertainty'):
        activities.append({'uuid': i.uuid, 'value': i.events[0].tags[0].value.value})


    return {'object': activities}

    #object = DBSession.query(A_Event).get(1)
    #return {'object':object.tags[0].key.language}

@view_config(route_name='geo_test', renderer='geojson')
def geo_test(request):
    return {
        'type': 'Feature',
        'id': 1,
        'geometry': {'type': 'Point', 'coordinates': [53, -4]},
        'properties': {'title': 'Dict 1'}
        }

@view_config(route_name='index', renderer='lmkp:templates/index.pt')
def index(request):
    """
    Returns the main HTML page
    """
    
    # Check if language (_LOCALE_) is set
    if request is not None and '_LOCALE_' in request.params:
        response = request.response
        response.set_cookie('_LOCALE_', request.params.get('_LOCALE_'))

    # Check if profile (_PROFILE_) is set
    if request is not None and '_PROFILE_' in request.params:
        response = request.response
        response.set_cookie('_PROFILE_', request.params.get('_PROFILE_'))

    # Check if the user is logged in
    username = authenticated_userid(request)
    # Assume the user is not logged in per default
    login = False
    if username is not None:
        login = True
    else:
        username = 'unknown user'
    return {'header': 'welcome', 'login': login, 'username': username, 'script': 'main'}

@view_config(route_name='ext_tests', renderer='lmkp:templates/tests.pt')
def ext_tests(request):
    return {}
