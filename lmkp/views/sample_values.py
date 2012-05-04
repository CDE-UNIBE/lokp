from pyramid.view import view_config

# import exceptions for sqlalchemy
from sqlalchemy.exc import IntegrityError
import transaction

from sqlalchemy import delete, or_

import random

from ..models.meta import DBSession as Session
from ..models.database_objects import *

@view_config(route_name='sample_values', renderer='lmkp:templates/sample_values.pt')
def sample_values(request):
    stack = []
    list_activities = []
    list_stakeholders = []
    #list_predefined_a_keys = []
    list_predefined_sh_keys = []
    list_users = []
    list_status = []
    #list_predefined_a_values_projectUse = []
    #list_predefined_a_values_projectStatus = []
# BEGIN fix data ----------------------------------------------------------------------------------
    stack.append('--- fix data ---')
    """
    # status
    count = []
    status1 = Status(id=1, name='pending', description='Review pending. Not published yet.')
    count.append(_add_to_db(status1, 'status 1 (pending)'))
    list_status.append(status1)
    status2 = Status(id=2, name='active', description='Reviewed and accepted. Currently published.')
    count.append(_add_to_db(status2, 'status 2 (active)'))
    list_status.append(status2)
    status3 = Status(id=3, name='overwritten', description='Overwritten. Not published anymore.')
    count.append(_add_to_db(status3, 'status 3 (overwritten'))
    list_status.append(status3)
    status4 = Status(id=4, name='deleted', description='Deleted. Not published anymore.')
    count.append(_add_to_db(status4, 'status 4 (deleted)'))
    list_status.append(status4)
    status5 = Status(id=5, name='rejected', description='Reviewed and rejected. Never published.')
    count.append(_add_to_db(status5, 'status 5 (rejected)'))
    list_status.append(status5)
    stack.append(str(count.count(1)) + ' status added.')
    """
    status1 = Session.query(Status).get(1)
    status2 = Session.query(Status).get(2)
    status3 = Session.query(Status).get(3)
    status4 = Session.query(Status).get(4)
    status5 = Session.query(Status).get(5)
    """
    # stakeholder_roles
    count = []
    sh_role1 = Stakeholder_Role(id=1, name='Donor')
    count.append(_add_to_db(sh_role1, 'stakeholder role 1 (donor)'))
    sh_role2 = Stakeholder_Role(id=2, name='Implementing agency')
    count.append(_add_to_db(sh_role2, 'stakeholder role 2 (implementing agency)'))
    sh_role3 = Stakeholder_Role(id=3, name='Partner')
    count.append(_add_to_db(sh_role3, 'stakeholder role 3 (partner)'))
    sh_role4 = Stakeholder_Role(id=4, name='Beneficiary')
    count.append(_add_to_db(sh_role4, 'stakeholder role 4 (beneficiary)'))
    sh_role5 = Stakeholder_Role(id=5, name='Informant')
    count.append(_add_to_db(sh_role5, 'stakeholder role 5 (informant)'))
    sh_role6 = Stakeholder_Role(id=6, name='Investor')
    count.append(_add_to_db(sh_role6, 'stakeholder role 6 (investor)'))
    stack.append(str(count.count(1)) + ' stakeholder_roles added.')
    """
    sh_role1 = Session.query(Stakeholder_Role).get(1)
    sh_role2 = Session.query(Stakeholder_Role).get(2)
    sh_role3 = Session.query(Stakeholder_Role).get(3)
    sh_role4 = Session.query(Stakeholder_Role).get(4)
    sh_role5 = Session.query(Stakeholder_Role).get(5)
    sh_role6 = Session.query(Stakeholder_Role).get(6)
    # languages
    count = []
    """
    lang1 = Language(id=1, english_name='English', local_name='English')
    count.append(_add_to_db(lang1, 'language 1 (english)'))
    """
    lang1 = Session.query(Language).get(1)
    lang2 = Language(id=2, english_name='Spanish', local_name='Espanol', locale='es')
    count.append(_add_to_db(lang2, 'language 2 (spanish)'))
    stack.append(str(count.count(1)) + ' languages added.')
    """
    # predefined a_keys (@todo: predefined keys should be managed in config file)
    count = []
    predefined_a_key1 = A_Key(key='Name')
    predefined_a_key1.language = lang1
    count.append(_add_to_db(predefined_a_key1, 'predefined a_key 1 (name)'))
    list_predefined_a_keys.append(predefined_a_key1)
    predefined_a_key2 = A_Key(key='Area')
    predefined_a_key2.language = lang1
    count.append(_add_to_db(predefined_a_key2, 'predefined a_key 2 (area)'))
    list_predefined_a_keys.append(predefined_a_key2)
    predefined_a_key3 = A_Key(key='Project Use')
    predefined_a_key3.language = lang1
    count.append(_add_to_db(predefined_a_key3, 'predefined a_key 3 (project_use)'))
    list_predefined_a_keys.append(predefined_a_key3)
    predefined_a_key4 = A_Key(key='Project Status')
    predefined_a_key4.language = lang1
    count.append(_add_to_db(predefined_a_key4, 'predefined a_key 4 (project_status)'))
    list_predefined_a_keys.append(predefined_a_key4)
    predefined_a_key5 = A_Key(key='Year of Investment')
    predefined_a_key5.language = lang1
    count.append(_add_to_db(predefined_a_key5, 'predefined a_key 5 (year_of_investment)'))
    list_predefined_a_keys.append(predefined_a_key5)
    stack.append(str(count.count(1)) + ' predefined a_keys added.')
    # predefined a_values (@todo: predefined values should be managed in config file)
    count = []
    predefined_a_value1 = A_Value(value='food production')
    predefined_a_value1.language = lang1
    count.append(_add_to_db(predefined_a_value1, 'predefined a_value 1 (food production'))
    list_predefined_a_values_projectUse.append(predefined_a_value1)
    predefined_a_value2 = A_Value(value='tourism')
    predefined_a_value2.language = lang1
    count.append(_add_to_db(predefined_a_value2, 'predefined a_value 2 (tourism'))
    list_predefined_a_values_projectUse.append(predefined_a_value2)
    predefined_a_value3 = A_Value(value='forestry for wood and fiber')
    predefined_a_value3.language = lang1
    count.append(_add_to_db(predefined_a_value3, 'predefined a_value 3 (forestry for wood and fiber'))
    list_predefined_a_values_projectUse.append(predefined_a_value3)
    predefined_a_value4 = A_Value(value='agrofuels')
    predefined_a_value4.language = lang1
    count.append(_add_to_db(predefined_a_value4, 'predefined a_value 4 (agrofuels'))
    list_predefined_a_values_projectUse.append(predefined_a_value4)
    predefined_a_value5 = A_Value(value='pending')
    predefined_a_value5.language = lang1
    count.append(_add_to_db(predefined_a_value5, 'predefined a_value 5 (pending'))
    list_predefined_a_values_projectStatus.append(predefined_a_value5)
    predefined_a_value6 = A_Value(value='signed')
    predefined_a_value6.language = lang1
    count.append(_add_to_db(predefined_a_value6, 'predefined a_value 6 (signed'))
    list_predefined_a_values_projectStatus.append(predefined_a_value6)
    predefined_a_value7 = A_Value(value='abandoned')
    predefined_a_value7.language = lang1
    count.append(_add_to_db(predefined_a_value7, 'predefined a_value 7 (abandoned'))
    list_predefined_a_values_projectStatus.append(predefined_a_value7)
    stack.append(str(count.count(1)) + ' predefined a_values added.')
    """
    list_predefined_a_keys = []
    for el in Session.query(A_Key).filter(A_Key.fk_a_key == None).all():
        list_predefined_a_keys.append(el)
    list_predefined_a_values_projectUse = []
    for el in Session.query(A_Value).filter(or_(A_Value.value.ilike('tourism%'), A_Value.value.ilike('forestry%'), A_Value.value.ilike('agrofuels%'), A_Value.value.ilike('food%'))).all():
        list_predefined_a_values_projectUse.append(el)
    list_predefined_a_values_projectStatus = []
    for el in Session.query(A_Value).filter(or_(A_Value.value.ilike('pending%'), A_Value.value.ilike('signed%'), A_Value.value.ilike('abandoned%'))):
        list_predefined_a_values_projectStatus.append(el)
    # predefined sh_keys (@todo: predefined keys should be managed in config file)
    count = []
    predefined_sh_key1 = SH_Key(key='First name')
    predefined_sh_key1.language = lang1
    count.append(_add_to_db(predefined_sh_key1, 'predefined sh_key 1 (first name)'))
    list_predefined_sh_keys.append(predefined_sh_key1)
    predefined_sh_key2 = SH_Key(key='Last name')
    predefined_sh_key2.language = lang1
    count.append(_add_to_db(predefined_sh_key2, 'predefined sh_key 2 (last name)'))
    list_predefined_sh_keys.append(predefined_sh_key2)
    stack.append(str(count.count(1)) + ' predefined sh_keys added.')
    # predefined sh_values (@todo: predefined values should be managed in config file)
    count = []
    predefined_sh_value1 = SH_Value(value='some sample sh_value')
    predefined_sh_value1.language = lang1
    count.append(_add_to_db(predefined_sh_value1, 'predefined sh_value 1 (sample value'))
    stack.append(str(count.count(1)) + ' predefined sh_values added.')
    """
    # permissions
    count = []
    permission1 = Permission(id=1, name='read')
    count.append(_add_to_db(permission1, 'permission 1 (read)'))
    permission2 = Permission(id=2, name='write')
    count.append(_add_to_db(permission2, 'permission 2 (write)'))
    stack.append(str(count.count(1)) + ' permissions added.')
    """
    """
    # groups (with permissions)
    count = []
    group1 = Group(id=1, name='editors')
    group1.permissions.append(permission1)
    group1.permissions.append(permission2)
    count.append(_add_to_db(group1, 'group 1 (editors)'))
    group2 = Group(id=2, name='moderators')
    group2.permissions.append(permission1)
    count.append(_add_to_db(group2, 'group 2 (moderators)'))
    stack.append(str(count.count(1)) + ' groups added.')
    """
    """
    # review_decisions
    count = []
    reviewdecision1 = Review_Decision(id=1, name='approved', description='Event or Involvement was approved.')
    count.append(_add_to_db(reviewdecision1, 'review decision 1 (approved)'))
    reviewdecision2 = Review_Decision(id=2, name='rejected', description='Event or Involvement was rejected.')
    count.append(_add_to_db(reviewdecision2, 'review decision 2 (rejected)'))
    reviewdecision3 = Review_Decision(id=3, name='deleted', description='Event or Involvement was deleted.')
    count.append(_add_to_db(reviewdecision3, 'review decision 3 (deleted)'))
    stack.append(str(count.count(1)) + ' review_decisions added.')
    """
    reviewdecision1 = Session.query(Review_Decision).get(1)
    reviewdecision2 = Session.query(Review_Decision).get(2)
    reviewdecision3 = Session.query(Review_Decision).get(3)
# END fix data ------------------------------------------------------------------------------------
# BEGIN sample data -------------------------------------------------------------------------------
    stack.append('--- sample data (users) ---')
  # -- users
    count = []
    """
    # user 1, belongs to admin group
    user1 = User(username='user1', password='pw', email='me@you.com')
    user1.groups.append(group1)
    count.append(_add_to_db(user1, 'user 1'))
    list_users.append(user1)
    """
    # add first user (by populate script) to list
    user1 = Session.query(User).filter(User.username == 'user1').one()
    list_users.append(user1)
    # user 2, belongs to user group
    user2 = User(username='user2', password='pw', email='you@me.com')
    user2.groups.append(Session.query(Group).get(2))
    count.append(_add_to_db(user2, 'user 2'))
    list_users.append(user2)
    stack.append(str(count.count(1)) + ' users added.')
# activities
    # random activities with status=active.
    count1 = []
    count2 = []
    stack.append('--- sample data (active activities) ---')
    for i in range(1,11):
        # switch
        switch = (i % len(list_predefined_a_keys))
        # prepare key
        theKey = list_predefined_a_keys[switch]
        # prepare value
        if (switch == 0): # project use
            theValue = random.choice(list_predefined_a_values_projectUse)
        if (switch == 1): # area
            theValue = A_Value(value=random.randint(1,100))
            theValue.language = lang1
        if (switch == 2): # project status
            theValue = random.choice(list_predefined_a_values_projectStatus)
        if (switch == 3): # name
            theValue = A_Value(value='Project ' + str(i))
            theValue.language = lang1
        if (switch == 4): # spatial uncertainty
            theValue = A_Value(value=random.choice(['small', 'medium', 'big']))
            theValue.language = lang1
        if (switch == 5): # year of investment
            theValue = A_Value(value=random.randint(1990,2020))
            theValue.language = lang1
        """
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
        """
        # prepare tag
        tag = A_Tag()
        tag.key = theKey
        tag.value = theValue
        # tag_group
        tag_group = A_Tag_Group()
        tag_group.tags.append(tag)
        tag_group.main_tag = tag
        # prepare changeset
        changeset = A_Changeset(source='[active] Source ' + str(i))
        changeset.user = random.choice(list_users)
        # prepare activity
        identifier = uuid.uuid4()
        activity = Activity(activity_identifier=identifier, version=1, point="POINT(" + str(random.randint(1,180)) + " " + str(random.randint(1,90)) + ")")
        activity.status = status2 # active
        activity.tag_groups.append(tag_group)
        activity.changesets.append(changeset)
        # insert activity
        count1.append(_add_to_db(activity, 'activity ' + str(i)))
        list_activities.append(activity)
        # prepare review
        review = A_Changeset_Review(comment='[active] Review_Comment ' + str(i))
        review.changeset = changeset
        review.user = user1     # always admin
        review.review_decision = reviewdecision1    # always approved
        count2.append(_add_to_db(review, 'review decision ' + str(i)))
    stack.append(str(len(count1)) + ' activities added.')
    stack.append(str(len(count2)) + ' review decisions added.')
    # random activities with 2 tags status=active.
    count1 = []
    count2 = []
    stack.append('--- sample data (active activities, 2 tags) ---')
    for i in range(11,21):
        # switch
        switch = (i % len(list_predefined_a_keys))
        # prepare key
        theKey = list_predefined_a_keys[switch]
        # prepare value
        if (switch == 0): # project use
            theValue = random.choice(list_predefined_a_values_projectUse)
        if (switch == 1): # area
            theValue = A_Value(value=random.randint(1,100))
            theValue.language = lang1
        if (switch == 2): # project status
            theValue = random.choice(list_predefined_a_values_projectStatus)
        if (switch == 3): # name
            theValue = A_Value(value='Project ' + str(i))
            theValue.language = lang1
        if (switch == 4): # spatial uncertainty
            theValue = A_Value(value=random.choice(['small', 'medium', 'big']))
            theValue.language = lang1
        if (switch == 5): # year of investment
            theValue = A_Value(value=random.randint(1990,2020))
            theValue.language = lang1
        # prepare tag
        tag = A_Tag()
        tag.key = theKey
        tag.value = theValue
        # tag_group
        tag_group = A_Tag_Group()
        tag_group.tags.append(tag)
        tag_group.main_tag = tag
        # add another tag_group
        switch = random.randint(0,len(list_predefined_a_keys)-1)
        theKey = list_predefined_a_keys[switch]
        if (switch == 0): # project use
            theValue = random.choice(list_predefined_a_values_projectUse)
        if (switch == 1): # area
            theValue = A_Value(value=random.randint(1,100))
            theValue.language = lang1
        if (switch == 2): # project status
            theValue = random.choice(list_predefined_a_values_projectStatus)
        if (switch == 3): # name
            theValue = A_Value(value='Project ' + str(i))
            theValue.language = lang1
        if (switch == 4): # spatial uncertainty
            theValue = A_Value(value=random.choice(['small', 'medium', 'big']))
            theValue.language = lang1
        if (switch == 5): # year of investment
            theValue = A_Value(value=random.randint(1990,2020))
            theValue.language = lang1
        tag = A_Tag()
        tag.key = theKey
        tag.value = theValue
        tag_group.tags.append(tag)
        # prepare changeset
        changeset = A_Changeset(source='[active] Source ' + str(i))
        changeset.user = random.choice(list_users)
        # prepare activity
        identifier = uuid.uuid4()
        activity = Activity(activity_identifier=identifier, version=1, point="POINT(" + str(random.randint(1,180)) + " " + str(random.randint(1,180)) + ")")
        activity.status = status2 # active
        activity.tag_groups.append(tag_group)
        activity.changesets.append(changeset)
        # insert activity
        count1.append(_add_to_db(activity, 'activity ' + str(i)))
        list_activities.append(activity)
        # prepare review
        review = A_Changeset_Review(comment='[active] Review_Comment ' + str(i))
        review.changeset = changeset
        review.user = user1     # always admin
        review.review_decision = reviewdecision1    # always approved
        count2.append(_add_to_db(review, 'review decision ' + str(i)))
    stack.append(str(len(count1)) + ' activities added.')
    stack.append(str(len(count2)) + ' review decisions added.')    
    # random activities with status=pending, no reviews
    count1 = []
    stack.append('--- sample data (pending activities) ---')
    for i in range(21,31):
        # switch
        switch = (i % len(list_predefined_a_keys))
        # prepare key
        theKey = list_predefined_a_keys[switch]
        # prepare value
        if (switch == 0): # project use
            theValue = random.choice(list_predefined_a_values_projectUse)
        if (switch == 1): # area
            theValue = A_Value(value=random.randint(1,100))
            theValue.language = lang1
        if (switch == 2): # project status
            theValue = random.choice(list_predefined_a_values_projectStatus)
        if (switch == 3): # name
            theValue = A_Value(value='Project ' + str(i))
            theValue.language = lang1
        if (switch == 4): # spatial uncertainty
            theValue = A_Value(value=random.choice(['small', 'medium', 'big']))
            theValue.language = lang1
        if (switch == 5): # year of investment
            theValue = A_Value(value=random.randint(1990,2020))
            theValue.language = lang1
        # prepare tag
        tag = A_Tag()
        tag.key = theKey
        tag.value = theValue
        # tag_group
        tag_group = A_Tag_Group()
        tag_group.tags.append(tag)
        tag_group.main_tag = tag
        # prepare changeset
        changeset = A_Changeset(source='[pending] Source ' + str(i))
        changeset.user = random.choice(list_users)
        # prepare activity
        identifier = uuid.uuid4()
        activity = Activity(activity_identifier=identifier, version=1, point="POINT(" + str(random.randint(1,180)) + " " + str(random.randint(1,180)) + ")")
        activity.status = status1 # pending
        activity.tag_groups.append(tag_group)
        activity.changesets.append(changeset)
        # insert activity
        count1.append(_add_to_db(activity, 'activity ' + str(i)))
    stack.append(str(len(count1)) + ' activities added.')
    # random activities with status=deleted.
    count1 = []
    count2 = []
    stack.append('--- sample data (deleted activities) ---')
    for i in range(31,41):
        # switch
        switch = (i % len(list_predefined_a_keys))
        # prepare key
        theKey = list_predefined_a_keys[switch]
        # prepare value
        if (switch == 0): # project use
            theValue = random.choice(list_predefined_a_values_projectUse)
        if (switch == 1): # area
            theValue = A_Value(value=random.randint(1,100))
            theValue.language = lang1
        if (switch == 2): # project status
            theValue = random.choice(list_predefined_a_values_projectStatus)
        if (switch == 3): # name
            theValue = A_Value(value='Project ' + str(i))
            theValue.language = lang1
        if (switch == 4): # spatial uncertainty
            theValue = A_Value(value=random.choice(['small', 'medium', 'big']))
            theValue.language = lang1
        if (switch == 5): # year of investment
            theValue = A_Value(value=random.randint(1990,2020))
            theValue.language = lang1
        # prepare tag
        tag = A_Tag()
        tag.key = theKey
        tag.value = theValue
        # tag_group
        tag_group = A_Tag_Group()
        tag_group.tags.append(tag)
        tag_group.main_tag = tag
        # prepare changeset
        changeset = A_Changeset(source='[deleted] Source ' + str(i))
        changeset.user = random.choice(list_users)
        # prepare activity
        identifier = uuid.uuid4()
        activity = Activity(activity_identifier=identifier, version=1, point="POINT(" + str(random.randint(1,180)) + " " + str(random.randint(1,180)) + ")")
        activity.status = status4 # deleted
        activity.tag_groups.append(tag_group)
        activity.changesets.append(changeset)
        # insert activity
        count1.append(_add_to_db(activity, 'activity ' + str(i)))
        # prepare review
        review = A_Changeset_Review(comment='[deleted] Review_Comment ' + str(i))
        review.changeset = changeset
        review.user = user1     # always admin
        review.review_decision = reviewdecision3    # deleted
        count2.append(_add_to_db(review, 'review decision ' + str(i)))
    stack.append(str(len(count1)) + ' activities added.')
    stack.append(str(len(count2)) + ' review decisions added.')
    # random activities with status=overwritten.
    count1 = []
    count2 = []
    count3 = []
    stack.append('--- sample data (overwritten activities) ---')
    for i in range(41,51):
        # switch
        switch = (i % len(list_predefined_a_keys))
        # prepare key
        theKey = list_predefined_a_keys[switch]
        # prepare value
        if (switch == 0): # project use
            theValue = random.choice(list_predefined_a_values_projectUse)
        if (switch == 1): # area
            theValue = A_Value(value=random.randint(1,100))
            theValue.language = lang1
        if (switch == 2): # project status
            theValue = random.choice(list_predefined_a_values_projectStatus)
        if (switch == 3): # name
            theValue = A_Value(value='Project ' + str(i))
            theValue.language = lang1
        if (switch == 4): # spatial uncertainty
            theValue = A_Value(value=random.choice(['small', 'medium', 'big']))
            theValue.language = lang1
        if (switch == 5): # year of investment
            theValue = A_Value(value=random.randint(1990,2020))
            theValue.language = lang1
        # prepare tag
        tag = A_Tag()
        tag.key = theKey
        tag.value = theValue
        # tag_group
        tag_group = A_Tag_Group()
        tag_group.tags.append(tag)
        tag_group.main_tag = tag
        # prepare changeset
        changeset = A_Changeset(source='[overwritten] Source ' + str(i))
        changeset.user = random.choice(list_users)
        # prepare activity
        identifier = uuid.uuid4()
        activity = Activity(activity_identifier=identifier, version=1, point="POINT(" + str(random.randint(1,180)) + " " + str(random.randint(1,180)) + ")")
        activity.status = status3 # deleted
        activity.tag_groups.append(tag_group)
        activity.changesets.append(changeset)
        #old_activity = activity
        # insert activity
        count1.append(_add_to_db(activity, 'activity ' + str(i)))
        # prepare review
        review = A_Changeset_Review(comment='[overwritten] Review_Comment ' + str(i))
        review.changeset = changeset
        review.user = user1     # always admin
        review.review_decision = reviewdecision1    # approved
        count3.append(_add_to_db(review, 'review decision ' + str(i)))
        # -- version 2
        new_activity = Activity(activity_identifier=identifier, version=2, point="POINT(" + str(random.randint(1,180)) + " " + str(random.randint(1,180)) + ")")
        new_activity.status = status2   # active
        new_tag_group = A_Tag_Group()
        switch = random.randint(0,len(list_predefined_a_keys)-1)
        newKey = list_predefined_a_keys[switch]
        if (switch == 0): # project use
            newValue = random.choice(list_predefined_a_values_projectUse)
        if (switch == 1): # area
            newValue = A_Value(value=random.randint(1,100))
            newValue.language = lang1
        if (switch == 2): # project status
            newValue = random.choice(list_predefined_a_values_projectStatus)
        if (switch == 3): # name
            newValue = A_Value(value='Project ' + str(i))
            newValue.language = lang1
        if (switch == 4): # spatial uncertainty
            newValue = A_Value(value=random.choice(['small', 'medium', 'big']))
            newValue.language = lang1
        if (switch == 5): # year of investment
            newValue = A_Value(value=random.randint(1990,2020))
            newValue.language = lang1
        new_tag = A_Tag()
        new_tag.key = newKey
        new_tag.value = newValue
        new_tag_group.activity = new_activity
        new_tag_group.tags.append(new_tag)
        new_tag_group.main_tag = new_tag
        # copy old key/value pairs
        session = Session()
        old_activity = session.query(Activity).filter(Activity.activity_identifier == identifier).first()
        for old_tag_group in old_activity.tag_groups:
           copy_tag_group = A_Tag_Group()
           for old_tag in old_tag_group.tags:
               copy_tag = A_Tag()
               copy_tag.fk_a_key = old_tag.fk_a_key
               copy_tag.fk_a_value = old_tag.fk_a_value
               copy_tag_group.tags.append(copy_tag)
           new_activity.tag_groups.append(copy_tag_group)
        # prepare changeset
        changeset = A_Changeset(source='[overwritten] Source ' + str(i))
        changeset.user = random.choice(list_users)
        new_activity.changesets.append(changeset)
        count2.append(_add_to_db(new_activity, 'activity ' + str(i)))
        list_activities.append(new_activity)
        # prepare review
        review = A_Changeset_Review(comment='[overwritten] Review_Comment ' + str(i))
        review.changeset = changeset
        review.user = user1     # always admin
        review.review_decision = reviewdecision1    # approved
        count3.append(_add_to_db(review, 'review decision ' + str(i)))
    stack.append(str(len(count1)) + ' activities added.')
    stack.append(str(len(count2)) + ' overwritten activities added.')
    stack.append(str(len(count3)) + ' review decisions added.')
# -- stakeholders
    # random stakeholders with status=active.
    count1 = []
    count2 = []
    stack.append('--- sample data (active stakeholders) ---')
    for i in range(1,21):
        # switch
        switch = (i % 2)
        theKey = list_predefined_sh_keys[switch]
        if (switch == 0): # first name
            theValue = SH_Value(value='First name ' + str(i))
            theValue.language = lang1
        if (switch == 1): # last name
            theValue = SH_Value(value='Last name ' + str(i))
            theValue.language = lang1
        # prepare tag
        tag = SH_Tag()
        tag.key = theKey
        tag.value = theValue
        # tag_group
        tag_group = SH_Tag_Group()
        tag_group.tags.append(tag)
        tag_group.main_tag = tag
        # prepare changeset
        changeset = SH_Changeset(source='[active] Source ' + str(i))
        changeset.user = random.choice(list_users)
        # prepare stakeholder
        identifier = uuid.uuid4()
        stakeholder = Stakeholder(stakeholder_identifier=identifier, version=1)
        stakeholder.status = status2 # active
        stakeholder.tag_groups.append(tag_group)
        stakeholder.changesets.append(changeset)
        # insert stakeholder
        count1.append(_add_to_db(stakeholder, 'stakeholder ' + str(i)))
        list_stakeholders.append(stakeholder)
        # prepare review
        review = SH_Changeset_Review(comment='[active] Review_Comment ' + str(i))
        review.changeset = changeset
        review.user = user1     # always admin
        review.review_decision = reviewdecision1    # always approved
        count2.append(_add_to_db(review, 'review decision ' + str(i)))
    stack.append(str(len(count1)) + ' stakeholders added.')
    stack.append(str(len(count2)) + ' review decisions added.')
# -- involvements (add each stakeholder to a random activity [active/overwritten])
    stack.append('--- sample data (involvements) ---')
    count1 = []
    for sh in list_stakeholders:
        inv = Involvement()
        inv.activity = random.choice(list_activities)
        inv.stakeholder = sh
        inv.stakeholder_role = sh_role4 # always Beneficiary
        count1.append(_add_to_db(inv, 'involvement'))
    stack.append(str(len(count1)) + ' involvements added.')
    return {'messagestack': stack}

@view_config(route_name='delete_sample_values', renderer='lmkp:templates/sample_values.pt')
def delete_sample_values(request):
# Trigger
    delete_fix_data = True
    stack = []
# BEGIN delete sample values ----------------------------------------------------------------------
    stack.append('--- sample data ---')
    inv_counter = 0
    all_involvements_beneficiary = Session.query(Involvement).filter(Involvement.fk_stakeholder_role == 4).all()
    for aib in all_involvements_beneficiary:
        inv_counter += 1
        Session.delete(aib)
    if (inv_counter > 0):
        stack.append(str(inv_counter) + ' involvements deleted.')
    all_a_reviews = Session.query(A_Changeset_Review).filter(or_(A_Changeset_Review.comment.like('[active] Review_Comment %'), A_Changeset_Review.comment.like('[overwritten] Review_Comment %'), A_Changeset_Review.comment.like('[deleted] Review_Comment %'), A_Changeset_Review.comment.like('[overwritten] Review_Comment %'))).all()
    rev_counter = 0
    for aar in all_a_reviews:
        rev_counter += 1
        Session.delete(aar)
    if (rev_counter > 0):
        stack.append(str(rev_counter) + " a_changeset_reviews deleted.")
    all_sh_reviews = Session.query(SH_Changeset_Review).filter(or_(SH_Changeset_Review.comment.like('[active] Review_Comment %'), SH_Changeset_Review.comment.like('[overwritten] Review_Comment %'), SH_Changeset_Review.comment.like('[deleted] Review_Comment %'), SH_Changeset_Review.comment.like('[overwritten] Review_Comment %'))).all()
    rev_counter = 0
    for asr in all_sh_reviews:
        rev_counter += 1
        Session.delete(asr)
    if (rev_counter > 0):
        stack.append(str(rev_counter) + " sh_changeset_reviews deleted.")
    all_activities = Session.query(Activity).join(A_Changeset).filter(or_(A_Changeset.source.like('[active] Source %'), A_Changeset.source.like('[pending] Source %'), A_Changeset.source.like('[overwritten] Source %'), A_Changeset.source.like('[deleted] Source %'), A_Changeset.source.like('[overwritten] Source %'))).all()
    act_counter = 0
    tag_counter = 0
    ch_counter = 0
    for aa in all_activities:
        # delete tag groups
        tag_groups = aa.tag_groups
        for tg in tag_groups:
            tags = tg.tags
            for t in tags:
                tag_counter += 1
                Session.delete(t)
            Session.delete(tg)
        # delete changesets
        changesets = aa.changesets
        for ch in changesets:
            ch_counter += 1
            Session.delete(ch)
        # delete activities
        act_counter += 1
        Session.delete(aa)
    if (tag_counter > 0 or act_counter > 0 or ch_counter > 0):
        stack.append(str(tag_counter) + " a_tags deleted.")
        stack.append(str(ch_counter) + " a_changesets deleted.")
        stack.append(str(act_counter) + " activities deleted.")
    all_stakeholders = Session.query(Stakeholder).join(SH_Changeset).filter(or_(SH_Changeset.source.like('[active] Source %'), SH_Changeset.source.like('[pending] Source %'), SH_Changeset.source.like('[overwritten] Source %'), SH_Changeset.source.like('[deleted] Source %'), SH_Changeset.source.like('[overwritten] Source %'))).all()
    sh_counter = 0
    tag_counter = 0
    ch_counter = 0
    for alls in all_stakeholders:
        # delete tag groups
        tag_groups = alls.tag_groups
        for tg in tag_groups:
            tags = tg.tags
            for t in tags:
                tag_counter += 1
                Session.delete(t)
            Session.delete(tg)
        # delete changesets
        changesets = alls.changesets
        for ch in changesets:
            ch_counter += 1
            Session.delete(ch)
        # delete activities
        sh_counter += 1
        Session.delete(alls)
    if (tag_counter > 0 or sh_counter > 0 or ch_counter > 0):
        stack.append(str(tag_counter) + " sh_tags deleted.")
        stack.append(str(ch_counter) + " sh_changesets deleted.")
        stack.append(str(act_counter) + " stakeholders deleted.")
# END delete sample values ------------------------------------------------------------------------
# -- BEGIN delete fix data ------------------------------------------------------------------------
    if (delete_fix_data):
        stack.append('--- fix data ---')
        # a_tags
        counter = 0
        all_a_keys = Session.query(A_Key).all()
        for ak in all_a_keys:
            Session.delete(ak)
            counter += 1
        if (counter > 0):
            stack.append(str(counter) + " a_keys deleted.")
        # a_values
        counter = 0
        all_a_values = Session.query(A_Value).all()
        for av in all_a_values:
            Session.delete(av)
            counter += 1
        if (counter > 0):
            stack.append(str(counter) + " a_values deleted.")
        # sh_tags
        counter = 0
        all_sh_keys = Session.query(SH_Key).all()
        for shk in all_sh_keys:
            Session.delete(shk)
            counter += 1
        if (counter > 0):
            stack.append(str(counter) + " sh_keys deleted.")
        # sh_values
        counter = 0
        all_sh_values = Session.query(SH_Value).all()
        for shv in all_sh_values:
            Session.delete(shv)
            counter += 1
        if (counter > 0):
            stack.append(str(counter) + " sh_values deleted.")
        # status
        counter = 0
        all_status = Session.query(Status).all()
        for status in all_status:
            Session.delete(status)
            counter += 1
        if (counter > 0):
            stack.append(str(counter) + " status deleted.")
        # stakeholder_roles
        counter = 0
        all_stakeholder_roles = Session.query(Stakeholder_Role).all()
        for sh_role in all_stakeholder_roles:
            Session.delete(sh_role)
            counter += 1
        if (counter > 0):
            stack.append(str(counter) + " stakeholder_roles deleted.")
        # groups
        counter = 0
        all_groups = Session.query(Group).all()
        for group in all_groups:
            Session.delete(group)
            counter += 1
        if (counter > 0):
            stack.append(str(counter) + " groups deleted.")
        # permissions
        counter = 0
        all_permissions = Session.query(Permission).all()
        for perm in all_permissions:
            Session.delete(perm)
            counter += 1
        if (counter > 0):
            stack.append(str(counter) + " permissions deleted.")
        # review_decisions
        counter = 0
        all_review_decisions = Session.query(Review_Decision).all()
        for revdec in all_review_decisions:
            Session.delete(revdec)
            counter += 1
        if (counter > 0):
            stack.append(str(counter) + " review_decisions deleted.")
        # languages
        counter = 0
        all_languages = Session.query(Language).all()
        for lang in all_languages:
            Session.delete(lang)
            counter += 1
        if (counter > 0):
            stack.append(str(counter) + " languages deleted.")
        # users
        counter = 0
        all_users = Session.query(User).all()
        for user in all_users:
            Session.delete(user)
            counter += 1
        if (counter > 0):
            stack.append(str(counter) + " users deleted.")
# END delete fix data -----------------------------------------------------------------------------
    if len(stack) == 0:
        stack.append('Nothing was deleted.')
    return {'messagestack':stack}

def _add_to_db(db_object, name):
    s = Session()
    s.add(db_object)
    try:
        transaction.commit()
        result = 1
    except IntegrityError:
        transaction.abort()
        result = 0
    return result