from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession
from pyramid.view import view_config
import uuid

#@view_config(route_name='home', renderer='../templates/mytemplate.pt')
def my_view(request):
# deleted from autocreated
#    one = DBSession.query(MyModel).filter(MyModel.name=='one').first()
#    return {'one':one, 'project':'MyProject'}
    return {'one':'one', 'project':'MyProject'}

@view_config(route_name='db_test', renderer='lmkp:templates/db_test.pt')
def db_test(request):

    from sqlalchemy import func, select
    from sqlalchemy import or_
    session1 = DBSession()
    
    #===========================================================================
    # # START OF TEST CASE to test database trigger preventing multiple 'active' activities
    # """
    # status1 = Status(id=1, name='status1')
    # status2 = Status(id=2, name='status2')
    # DBSession.add_all([status1, status2])
    # """
    # """
    # s1 = DBSession.query(Status).get(1)
    # s2 = DBSession.query(Status).get(2)
    # id1 = "c32212f8-e704-48e3-94bc-5670cfd01884"
    # id2 = "a6780ba4-bbd3-47e6-b739-6b7f29584272"
    # """
    # # add activity1 with status=1
    # """
    # a1 = Activity(activity_identifier=id1, version=1, point="POINT (10 20)")
    # a1.status = s1
    # DBSession.add(a1)
    # """
    # # update activity1 to status=2
    # """
    # a1 = DBSession.query(Activity).get(2)
    # a1.status = s2
    # import transaction
    # transaction.commit()
    # """
    # # add activity2 directly with status=2
    # """
    # a2 = Activity(activity_identifier=id2, version=1, point="POINT (10 20)")
    # a2.status = s2
    # DBSession.add(a2)
    # """
    # # try to add new version of activity1, also with status=2 (SHOULD FAIL)
    # """
    # a3 = Activity(activity_identifier=id1, version=2, point="POINT (10 20)")
    # a3.status = s2
    # DBSession.add(a3)
    # """
    # # the same version can be inserted if status != 2
    # """
    # a3 = Activity(activity_identifier=id1, version=2, point="POINT (10 20)")
    # a3.status = s1
    # DBSession.add(a3)
    # """
    # # it cannot be updated afterwards to status=2
    # """
    # a3 = DBSession.query(Activity).get(5)
    # a3.status = s2
    # import transaction
    # transaction.commit()
    # """
    # # END OF TEST CASE
    #===========================================================================
    
    #===========================================================================
    # # START OF TEST CASE to test main_tags
    # # some test values
    # id1 = "c32212f8-e704-48e3-94bc-5670cfd01884"
    # s1 = DBSession.query(Status).get(1)
    # k1 = DBSession.query(A_Key).get(1)
    # k2 = DBSession.query(A_Key).get(2)
    # v1 = DBSession.query(A_Value).get(1)
    # v2 = DBSession.query(A_Value).get(2)
    # 
    # # add an activity with a tag group that contains a main tag
    # """
    # t1 = A_Tag()
    # t1.key = k1
    # t1.value = v1
    # 
    # t2 = A_Tag()
    # t2.key = k2
    # t2.value = v2
    # 
    # tg1 = A_Tag_Group()
    # tg1.tags = [t1, t2]
    # tg1.main_tag = t1
    # 
    # a1 = Activity(activity_identifier=id1, version=1, point="POINT (10 20)")
    # a1.status = s1
    # a1.tag_groups = [tg1]
    # 
    # DBSession.add(a1)
    # """
    # 
    # # test it by querying it
    # """
    # q = DBSession.query(Activity).filter(Activity.activity_identifier == id1).first()
    # object = q.tag_groups[0].main_tag
    # """
    #===========================================================================
    
    object = "done"
    return {'object': object}

@view_config(route_name='geo_test', renderer='geojson')
def geo_test(request):
    return {
        'type': 'Feature',
        'id': 1,
        'geometry': {'type': 'Point', 'coordinates': [53, -4]},
        'properties': {'title': 'Dict 1'}
        }

@view_config(route_name='index', renderer='lmkp:templates/index.mak')
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

    return {'script': 'main'}

@view_config(route_name='ext_tests', renderer='lmkp:templates/tests.pt')
def ext_tests(request):
    return {}
