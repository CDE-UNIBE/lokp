from pyramid.view import view_config

# import exceptions for sqlalchemy
from sqlalchemy.exc import IntegrityError
import transaction

from sqlalchemy import delete

import random

from ..models.meta import DBSession as Session
from ..models.database_objects import *

@view_config(route_name='sample_values', renderer='lmkp:templates/sample_values.pt')
def sample_values(request):
    stack = []
    list_activities = []
    list_stakeholders = []
    list_predefined_a_keys = []
    list_predefined_sh_keys = []
    list_users = []
    list_status = []
    list_predefined_a_values_projectUse = []
    list_predefined_a_values_projectStatus = []
# BEGIN fix data ----------------------------------------------------------------------------------
    stack.append('--- fix data ---')
    # status
    status1 = Status(id=1, name='pending', description='Review pending. Not published yet.')
    stack.append(_add_to_db(status1, 'status 1 (pending)'))
    list_status.append(status1)
    status2 = Status(id=2, name='active', description='Reviewed and accepted. Currently published.')
    stack.append(_add_to_db(status2, 'status 2 (active)'))
    list_status.append(status2)
    status3 = Status(id=3, name='overwritten', description='Overwritten. Not published anymore.')
    stack.append(_add_to_db(status3, 'status 3 (overwritten'))
    list_status.append(status3)
    status4 = Status(id=4, name='rejected', description='Reviewed and rejected. Never published.')
    stack.append(_add_to_db(status4, 'status 4 (rejected)'))
    list_status.append(status4)
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
    # languages
    lang1 = Language(id=1, english_name='English', local_name='English')
    stack.append(_add_to_db(lang1, 'language 1 (english)'))
    lang2 = Language(id=2, english_name='Spanish', local_name='Espanol')
    stack.append(_add_to_db(lang2, 'language 2 (spanish)'))
    # predefined a_keys (@todo: predefined keys should be managed in config file)
    predefined_a_key1 = A_Key(key='name')
    predefined_a_key1.language = lang1
    stack.append(_add_to_db(predefined_a_key1, 'predefined a_key 1 (name)'))
    list_predefined_a_keys.append(predefined_a_key1)
    predefined_a_key2 = A_Key(key='area')
    predefined_a_key2.language = lang1
    stack.append(_add_to_db(predefined_a_key2, 'predefined a_key 2 (area)'))
    list_predefined_a_keys.append(predefined_a_key2)
    predefined_a_key3 = A_Key(key='project_use')
    predefined_a_key3.language = lang1
    stack.append(_add_to_db(predefined_a_key3, 'predefined a_key 3 (project_use)'))
    list_predefined_a_keys.append(predefined_a_key3)
    predefined_a_key4 = A_Key(key='project_status')
    predefined_a_key4.language = lang1
    stack.append(_add_to_db(predefined_a_key4, 'predefined a_key 4 (project_status)'))
    list_predefined_a_keys.append(predefined_a_key4)
    predefined_a_key5 = A_Key(key='year_of_investment')
    predefined_a_key5.language = lang1
    stack.append(_add_to_db(predefined_a_key5, 'predefined a_key 5 (year_of_investment)'))
    list_predefined_a_keys.append(predefined_a_key5)
    # predefined a_values (@todo: predefined values should be managed in config file)
    predefined_a_value1 = A_Value(value='food production')
    predefined_a_value1.language = lang1
    stack.append(_add_to_db(predefined_a_value1, 'predefined a_value 1 (food production'))
    list_predefined_a_values_projectUse.append(predefined_a_value1)
    predefined_a_value2 = A_Value(value='tourism')
    predefined_a_value2.language = lang1
    stack.append(_add_to_db(predefined_a_value2, 'predefined a_value 2 (tourism'))
    list_predefined_a_values_projectUse.append(predefined_a_value2)
    predefined_a_value3 = A_Value(value='forestry for wood and fiber')
    predefined_a_value3.language = lang1
    stack.append(_add_to_db(predefined_a_value3, 'predefined a_value 3 (forestry for wood and fiber'))
    list_predefined_a_values_projectUse.append(predefined_a_value3)
    predefined_a_value4 = A_Value(value='agrofuels')
    predefined_a_value4.language = lang1
    stack.append(_add_to_db(predefined_a_value4, 'predefined a_value 4 (agrofuels'))
    list_predefined_a_values_projectUse.append(predefined_a_value4)
    predefined_a_value5 = A_Value(value='pending')
    predefined_a_value5.language = lang1
    stack.append(_add_to_db(predefined_a_value5, 'predefined a_value 5 (pending'))
    list_predefined_a_values_projectStatus.append(predefined_a_value5)
    predefined_a_value6 = A_Value(value='signed')
    predefined_a_value6.language = lang1
    stack.append(_add_to_db(predefined_a_value6, 'predefined a_value 6 (signed'))
    list_predefined_a_values_projectStatus.append(predefined_a_value6)
    predefined_a_value7 = A_Value(value='abandoned')
    predefined_a_value7.language = lang1
    stack.append(_add_to_db(predefined_a_value7, 'predefined a_value 7 (abandoned'))
    list_predefined_a_values_projectStatus.append(predefined_a_value7)
    # predefined sh_keys (@todo: predefined keys should be managed in config file)
    predefined_sh_key1 = SH_Key(key='First name')
    predefined_sh_key1.language = lang1
    stack.append(_add_to_db(predefined_sh_key1, 'predefined a_key 1 (first name)'))
    list_predefined_sh_keys.append(predefined_sh_key1)
    predefined_sh_key2 = SH_Key(key='Last name')
    predefined_sh_key2.language = lang1
    stack.append(_add_to_db(predefined_sh_key2, 'predefined a_key 2 (last name)'))
    list_predefined_sh_keys.append(predefined_sh_key2)
    # predefined sh_values (@todo: predefined values should be managed in config file)
    predefined_sh_value1 = SH_Value(value='some sample sh_value')
    predefined_sh_value1.language = lang1
    stack.append(_add_to_db(predefined_sh_value1, 'predefined sh_value 1 (sample value'))
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
    stack.append('--- sample data (users) ---')
  # -- users
    # user 1, belongs to admin group
    user1 = User(username='user1', password='pw', email='me@you.com')
    user1.groups.append(group1)
    stack.append(_add_to_db(user1, 'user 1'))
    list_users.append(user1)
    # user 2, belongs to user group
    user2 = User(username='user2', password='pw', email='you@me.com')
    user2.groups.append(group2)
    stack.append(_add_to_db(user2, 'user 2'))
    list_users.append(user2)
# activities (create 25 random)
    stack.append('--- sample data (activities) ---')
    for i in range(1,26):
        activity = Activity()
        stack.append(_add_to_db(activity, 'activity ' + str(i)))
        list_activities.append(activity)
# a_events (create 100 random), with sample values (of config file), reported by random user, associated with one of activities, all reviewed and approved by user1 (admin)
# the first 5 are unattached
    stack.append('--- sample data (a_events) ---')
    for i in range(1,101):
        switch = (i % 5)
        theKey = list_predefined_a_keys[switch]
        if (switch == 0): # name
            theValue = A_Value(value='Project ' + str(i))
            theValue.language = lang1
        if (switch == 1): # area
            theValue = A_Value(value=random.randint(1,100))
            theValue.language = lang1
        if (switch == 2): # project_use
            theValue = random.choice(list_predefined_a_values_projectUse)
        if (switch == 3): # project_status
            theValue = random.choice(list_predefined_a_values_projectStatus)
        if (switch == 4): # year_of_investment
            theValue = A_Value(value=random.randint(1990, 2015))
            theValue.language = lang1
        a_tag = A_Tag()
        a_tag.key = theKey
        a_tag.value = theValue
        a_event = A_Event(geometry="POINT(" + str(random.randint(1,180)) + " " + str(random.randint(1,180)) + ")", source="source " + str(i))
        if (i > 6): # do not attach the first 5 events
            a_event.activity = random.choice(list_activities)
        a_event.user = random.choice(list_users)
        a_event.status = status2 # always approved
        a_event.tags.append(a_tag)
        stack.append(_add_to_db(a_event, 'a_event ' + str(i)))
        review = A_Event_Review(comment='comment ' + str(i))
        review.review_decision = reviewdecision1 # always approved
        review.user = user1 # always admin
        review.event = a_event
        stack.append(_add_to_db(review, 'review ' + str(i)))
# -- stakeholders (create 5 random)
    stack.append('--- sample data (stakeholders) ---')
    for i in range(1,6):
        stakeholder = Stakeholder()
        stack.append(_add_to_db(stakeholder, 'stakeholder ' + str(i)))
        list_stakeholders.append(stakeholder)
# -- sh_events (create 20 random), so far only first- and lastname, reported by random user, associated with one of stakeholders, all reviewed and approved by user1 (admin)
# the first 5 are unattached
    stack.append('--- sample data (sh_events) ---')
    for i in range(1,21):
        switch = (i % 2)
        theKey = list_predefined_sh_keys[switch]
        if (switch == 0): # first name
            theValue = SH_Value(value='First name ' + str(i))
            theValue.language = lang1
        if (switch == 1): # last name
            theValue = SH_Value(value='Last name ' + str(i))
            theValue.language = lang1
        sh_tag = SH_Tag()
        sh_tag.key = theKey
        sh_tag.value = theValue
        sh_event = SH_Event(source='source 1' + str(i))
        if (i > 6): # do not attach the first 5 events
            sh_event.stakeholder = random.choice(list_stakeholders)
        sh_event.user = random.choice(list_users)
        sh_event.status = status2 # always approved
        sh_event.tags.append(sh_tag)
        stack.append(_add_to_db(sh_event, 'sh_event ' + str(i)))
        review = SH_Event_Review(comment='comment ' + str(i))
        review.review_decision = reviewdecision1 # always approved
        review.user = user1 # always admin
        review.event = sh_event
        stack.append(_add_to_db(review, 'review ' + str(i)))
# -- involvements (add each stakeholder to a random activity)
    stack.append('--- sample data (involvements) ---')
    for sh in list_stakeholders:
        inv = Involvement()
        inv.activity = random.choice(list_activities)
        inv.stakeholder = sh
        inv.stakeholder_role = sh_role4 # always Beneficiary
        stack.append(_add_to_db(inv, 'involvement'))
    return {'messagestack': stack}

@view_config(route_name='delete_sample_values', renderer='lmkp:templates/sample_values.pt')
def delete_sample_values(request):
# Trigger
    delete_fix_data = True
    stack = []
# BEGIN delete sample values ----------------------------------------------------------------------
    stack.append('--- sample data (reviews) ---')
    all_a_reviews = Session.query(A_Event_Review).filter(A_Event_Review.comment.like('comment %')).all()
    for aar in all_a_reviews:
        stack.append("deleted: a_event_review")
        Session.delete(aar)
    all_sh_reviews = Session.query(SH_Event_Review).filter(SH_Event_Review.comment.like('comment %')).all()
    for asr in all_sh_reviews:
        stack.append("deleted: sh_event_review")
        Session.delete(asr)
    stack.append('--- sample data (involvements) ---')
    all_involvements_beneficiary = Session.query(Involvement).filter(Involvement.fk_stakeholder_role == 4).all()
    for aib in all_involvements_beneficiary:
        stack.append("deleted: involvement with stakeholder_role 4 (Beneficiary)")
        Session.delete(aib)
    stack.append('--- sample data (a_events) ---')
    all_a_events_source1 = Session.query(A_Event).filter(A_Event.source.like('source %')).all()
    for aaes1 in all_a_events_source1:
        stack.append("deleted: a_event")
        Session.delete(aaes1)
    stack.append('--- sample data (sh_events) ---')
    all_sh_events_source1 = Session.query(SH_Event).filter(SH_Event.source.like('source %')).all()
    for ases1 in all_sh_events_source1:
        stack.append("deleted: sh_event")
        Session.delete(ases1)
    stack.append('--- sample data (users) ---')
    del_user1 = Session.query(User).filter(User.username == 'user1').all()
    for du1 in del_user1:
        stack.append("deleted: user 1")
        Session.delete(du1)
    del_user2 = Session.query(User).filter(User.username == 'user2').all()
    for du2 in del_user2:
        stack.append("deleted: user 2")
        Session.delete(du2)
    # delete orphan activities (should possibly be done by trigger on database level)
    stack.append('--- sample data (activities) ---')
    all_orphan_activities = Session.query(Activity).filter(~Activity.id.in_(Session.query(A_Event.fk_activity))).all()
    for aoa in all_orphan_activities:
        stack.append("deleted: activity")
        Session.delete(aoa)
    # delete orphan stakeholders (should possibly be done by trigger on database level)
    stack.append('--- sample data (stakeholders) ---')
    all_orphan_stakeholders = Session.query(Stakeholder).filter(~Stakeholder.id.in_(Session.query(SH_Event.fk_stakeholder))).all()
    for aos in all_orphan_stakeholders:
        stack.append("deleted: orphan stakeholder")
        Session.delete(aos)
# END delete sample values ------------------------------------------------------------------------
# -- BEGIN delete fix data ------------------------------------------------------------------------
    if (delete_fix_data):
        stack.append('--- fix data (reviews) ---')
        # a_tags
        all_a_keys = Session.query(A_Key).all()
        for ak in all_a_keys:
            stack.append("deleted: a_key " + ak.key)
            Session.delete(ak)
        # a_values
        all_a_values = Session.query(A_Value).all()
        for av in all_a_values:
            stack.append("deleted: a_value " + av.value)
            Session.delete(av)
        # sh_tags
        all_sh_keys = Session.query(SH_Key).all()
        for shk in all_sh_keys:
            stack.append("deleted: sh_key " + shk.key)
            Session.delete(shk)
        # sh_values
        all_sh_values = Session.query(SH_Value).all()
        for shv in all_sh_values:
            stack.append("deleted: sh_value " + shv.value)
            Session.delete(shv)
        # status
        all_status = Session.query(Status).all()
        for status in all_status:
            stack.append("deleted: status " + status.name)
            Session.delete(status)
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
        # languages
        all_languages = Session.query(Language).all()
        for lang in all_languages:
            stack.append("deleted: language " + lang.english_name)
            Session.delete(lang)
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

