from pyramid.view import view_config

# import exceptions for sqlalchemy
from sqlalchemy.exc import IntegrityError
import transaction

from sqlalchemy import delete

from ..models.meta import DBSession as Session
from ..models.database_objects import *
from chameleon.nodes import Attribute


@view_config(route_name='sample_values', renderer='myproject:templates/sample_values.pt')
def sample_values(request):
    stack = []
# BEGIN fix data ----------------------------------------------------------------------------------
    # status
    status1 = Status(id=1, name='pending', description='Review pending. Not published yet.')
    stack.append(_add_to_db(status1, 'status 1 (pending)'))
    status2 = Status(id=2, name='active', description='Reviewed and accepted. Currently published.')
    stack.append(_add_to_db(status2, 'status 2 (active)'))
    status3 = Status(id=3, name='overwritten', description='Overwritten. Not published anymore.')
    stack.append(_add_to_db(status3, 'status 3 (overwritten'))
    status4 = Status(id=4, name='rejected', description='Reviewed and rejected. Never published.')
    stack.append(_add_to_db(status4, 'status 4 (rejected)'))
    # stakeholder_roles
    sh_role1 = Stakeholder_Role(id=1, name='Donor')
    stack.append(_add_to_db(sh_role1, 'stakeholder role 1 (donor)'))
    sh_role2 = Stakeholder_Role(id=2, name='Implementing agency')
    stack.append(_add_to_db(sh_role2, 'stakeholder role 2 (implementing agency)'))
    sh_role3 = Stakeholder_Role(id=3, name='Partner')
    stack.append(_add_to_db(sh_role3, 'stakeholder role 3 (partner)'))
    sh_role4 = Stakeholder_Role(id=4, name='Beneficiary')
    stack.append(_add_to_db(sh_role4, 'stakeholder role 4 (beneficiary)'))
    sh_role5 = Stakeholder_Role(id=5, name='Informant')
    stack.append(_add_to_db(sh_role5, 'stakeholder role 5 (informant)'))
    sh_role6 = Stakeholder_Role(id=6, name='Investor')
    stack.append(_add_to_db(sh_role6, 'stakeholder role 6 (investor)'))
    # fixed_events
    fixed_a_tag1 = Fixed_A_Tag(code='spatial_uncertainty', category='geometry')
    stack.append(_add_to_db(fixed_a_tag1, 'fixed event 1 (spatial uncertainty)'))
    # fixed_attributes
    fixed_sh_tag1 = Fixed_SH_Tag(code='firstname', category='individual')
    stack.append(_add_to_db(fixed_sh_tag1, 'fixed attribute 1 (firstname)'))
    # permissions
    permission1 = Permission(id=1, name='read')
    stack.append(_add_to_db(permission1, 'permission 1 (read)'))
    permission2 = Permission(id=2, name='write')
    stack.append(_add_to_db(permission2, 'permission 2 (write)'))
    # groups (with permissions)
    group1 = Group(id=1, name='Admin')
    group1.permissions.append(permission1)
    group1.permissions.append(permission2)
    stack.append(_add_to_db(group1, 'group 1 (admin)'))
    group2 = Group(id=2, name='User')
    group2.permissions.append(permission1)
    stack.append(_add_to_db(group2, 'group 2 (user)'))
    # review_decisions
    reviewdecision1 = Review_Decision(id=1, name='approved', description='Event or Involvement was approved.')
    stack.append(_add_to_db(reviewdecision1, 'review decision 1 (approved)'))
    reviewdecision2 = Review_Decision(id=2, name='rejected', description='Event or Involvement was rejected.')
    stack.append(_add_to_db(reviewdecision2, 'review decision 2 (rejected)'))
    reviewdecision3 = Review_Decision(id=3, name='deleted', description='Event or Involvement was deleted.')
    stack.append(_add_to_db(reviewdecision3, 'review decision 3 (deleted)'))
# END fix data ------------------------------------------------------------------------------------
# BEGIN sample data -------------------------------------------------------------------------------
  # -- users
    # user 1, belongs to admin group
    user1 = User(username='user1', password='pw', email='me@you.com')
    user1.groups.append(group1)
    stack.append(_add_to_db(user1, 'user 1'))
    # user 2, belongs to user group
    user2 = User(username='user2', password='pw', email='you@me.com')
    user2.groups.append(group2)
    stack.append(_add_to_db(user2, 'user 2'))
# -- activities
    # activity 1
    activity1 = Activity()
    stack.append(_add_to_db(activity1, 'activity 1'))
# -- a_events (activity events)
    # a_event 1, belongs to activity 1, inserted by user 2, reviewed (and accepted) by user 1
    a_event1 = A_Event(geometry="POINT(10 20)", source='source1')
    a_event1.activity = activity1
    a_event1.user = user2
    a_event1.status = status2 # active
    a_event1.tags.append(A_Tag(key='spatial_uncertainty', value='very inaccurate'))
    stack.append(_add_to_db(a_event1, 'a_event 1'))
    review1 = A_Event_Review(comment='comment1')
    review1.review_decision = reviewdecision1 # approved
    review1.user = user1
    review1.event = a_event1
    stack.append(_add_to_db(review1, 'review 1')) 
# -- stakeholders
    # stakeholder 1
    stakeholder1 = Stakeholder()
    stack.append(_add_to_db(stakeholder1, 'stakeholder 1'))
# -- sh_events (stakeholder events)
    # sh_event 1, belongs to stakeholder 1, inserted by user 2, unreviewed
    sh_event1 = SH_Event(source='source1')
    sh_event1.stakeholder = stakeholder1
    sh_event1.user = user2
    sh_event1.status = status1 # pending
    sh_event1.tags.append(SH_Tag(key='firstname', value='Hans'))
    sh_event1.tags.append(SH_Tag(key='lastname', value='Muster'))
    stack.append(_add_to_db(sh_event1, 'sh_event 1'))
# -- involvements
    # involvement 1, connects activity 1 with stakeholder 1
    inv1 = Involvement()
    inv1.activity = activity1
    inv1.stakeholder = stakeholder1
    inv1.stakeholder_role = sh_role4 # Beneficiary
    stack.append(_add_to_db(inv1, 'involvement 1'))
    return {'messagestack': stack}

@view_config(route_name='delete_sample_values', renderer='myproject:templates/sample_values.pt')
def delete_sample_values(request):
# Trigger
    delete_fix_data = True
    stack = []
# BEGIN delete sample values ----------------------------------------------------------------------
    all_a_reviews = Session.query(A_Event_Review).filter(A_Event_Review.comment == 'comment1').all()
    for aar in all_a_reviews:
        stack.append("deleted: a_event_review")
        Session.delete(aar)
    all_involvements_beneficiary = Session.query(Involvement).filter(Involvement.fk_stakeholder_role == 4).all()
    for aib in all_involvements_beneficiary:
        stack.append("deleted: involvement with stakeholder_role 4 (Beneficiary)")
        Session.delete(aib)
    all_a_events_source1 = Session.query(A_Event).filter(A_Event.source == 'source1').all()
    for aaes1 in all_a_events_source1:
        stack.append("deleted: a_event with source 1")
        Session.delete(aaes1)
    all_sh_events_source1 = Session.query(SH_Event).filter(SH_Event.source == 'source1').all()
    for ases1 in all_sh_events_source1:
        stack.append("deleted: sh_event with source 1")
        Session.delete(ases1)
    del_user1 = Session.query(User).filter(User.username == 'user1').all()
    for du1 in del_user1:
        stack.append("deleted: user 1")
        Session.delete(du1)
    del_user2 = Session.query(User).filter(User.username == 'user2').all()
    for du2 in del_user2:
        stack.append("deleted: user 2")
        Session.delete(du2)
    # delete orphan activities (should possibly be done by trigger on database level)
    all_orphan_activities = Session.query(Activity).filter(~Activity.id.in_(Session.query(A_Event.fk_activity))).all()
    for aoa in all_orphan_activities:
        stack.append("deleted: orphan activity")
        Session.delete(aoa)
    # delete orphan stakeholders (should possibly be done by trigger on database level)
    all_orphan_stakeholders = Session.query(Stakeholder).filter(~Stakeholder.id.in_(Session.query(SH_Event.fk_stakeholder))).all()
    for aos in all_orphan_stakeholders:
        stack.append("deleted: orphan stakeholder")
        Session.delete(aos)
# END delete sample values ------------------------------------------------------------------------
# -- BEGIN delete fix data ------------------------------------------------------------------------
    if (delete_fix_data):
        # fixed_a_tags
        all_fixed_a_tags = Session.query(Fixed_A_Tag).all()
        for fixed_event in all_fixed_a_tags:
            stack.append("deleted: fixed event " + fixed_event.code)
            Session.delete(fixed_event)
        # status
        all_status = Session.query(Status).all()
        for status in all_status:
            stack.append("deleted: status " + status.name)
            Session.delete(status)
        # fixed_sh_tags
        all_fixed_sh_tags = Session.query(Fixed_SH_Tag).all()
        for fixed_attr in all_fixed_sh_tags:
            stack.append("deleted: fixed attribute " + fixed_attr.code)
            Session.delete(fixed_attr)
        # stakeholder_roles
        all_stakeholder_roles = Session.query(Stakeholder_Role).all()
        for sh_role in all_stakeholder_roles:
            stack.append("deleted: stakeholder role " + sh_role.name)
            Session.delete(sh_role)
        # groups
        all_groups = Session.query(Group).all()
        for group in all_groups:
            stack.append("deleted: group " + group.name)
            Session.delete(group)
        # permissions
        all_permissions = Session.query(Permission).all()
        for perm in all_permissions:
            stack.append("deleted: permission " + perm.name)
            Session.delete(perm)
        # review_decisions
        all_review_decisions = Session.query(Review_Decision).all()
        for revdec in all_review_decisions:
            stack.append("deleted: review decision " + revdec.name)
            Session.delete(revdec)
# END delete fix data -----------------------------------------------------------------------------
    if len(stack) == 0:
        stack.append('Nothing was deleted.')
    return {'messagestack':stack}

def _add_to_db(db_object, name):
    Session.add(db_object)
    try:
        transaction.commit()
        result = 'added: ' + name
    except IntegrityError:
        transaction.abort()
        result = 'not added: ' + name
    return result

