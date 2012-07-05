from lmkp.models.database_objects import Activity
from lmkp.models.database_objects import Language
from lmkp.models.database_objects import Involvement
from lmkp.models.database_objects import SH_Changeset
from lmkp.models.database_objects import SH_Key
from lmkp.models.database_objects import SH_Tag
from lmkp.models.database_objects import SH_Tag_Group
from lmkp.models.database_objects import SH_Value
from lmkp.models.database_objects import Stakeholder
from lmkp.models.database_objects import Stakeholder_Role
from lmkp.models.database_objects import Status
from lmkp.models.database_objects import User
from lmkp.views.protocol import Feature
from lmkp.views.protocol import Protocol
from lmkp.views.protocol import Tag
from lmkp.views.protocol import TagGroup
from lmkp.views.protocol import Inv
import logging
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPCreated
from pyramid.i18n import get_localizer
from sqlalchemy import func
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql.expression import asc
from sqlalchemy.sql.expression import desc
from sqlalchemy.types import Float
import uuid



log = logging.getLogger(__name__)

class StakeholderProtocol(Protocol):

    def __init__(self, Session):
        self.Session = Session

    def create(self, request):

        raw = request.json_body

        # Check if the json body is a valid diff file
        #if 'create' not in raw and 'modify' not in raw and 'delete' not in raw:
        if 'stakeholders' not in raw:
            return HTTPBadRequest(detail="Not a valid format")

        ids = []
        for stakeholder in raw['stakeholders']:
            ids.append(self._handle_stakeholder(request, stakeholder))

        # Return the newly created object with 201 Created HTTP code status
        #return HTTPCreated(detail='Ok')
        return ids

    def _handle_stakeholder(self, request, stakeholder_dict, status='pending'):

        # Collect information about changing involvements
        involvement_change = stakeholder_dict['activities'] if 'activities' in stakeholder_dict else None
        implicit_inv_change = True if involvement_change is not None and 'implicit_involvement_update' in stakeholder_dict and stakeholder_dict['implicit_involvement_update'] is True else False

        # If this stakeholder does not have an id then create a new stakeholder
        if 'id' not in stakeholder_dict:
            new_stakeholder = self._create_stakeholder(request, stakeholder_dict, status=status)
            
            # Handle involvements
            self._handle_involvements(request, None, new_stakeholder, involvement_change, implicit_inv_change)
            
            return new_stakeholder 

        # Get the identifier from the request
        identifier = stakeholder_dict['id']
        old_version = stakeholder_dict['version'] if 'version' in stakeholder_dict else None

        # Try to get the stakeholder from the database with this id
        db_sh = self.Session.query(Stakeholder).\
            filter(Stakeholder.stakeholder_identifier == identifier).\
            filter(Stakeholder.version == old_version).\
            first()

        # If no stakeholder is found, create a new stakeholder
        if db_sh == None:
            new_stakeholder = self._create_stakeholder(request, stakeholder_dict, identifier=identifier, status=status) 
            
            # Handle involvements
            self._handle_involvements(request, None, new_stakeholder, involvement_change, implicit_inv_change)
            
            return new_stakeholder

        # Update the stakeholder:
        # The basic idea is to deep copy the previous version and control during
        # the copying if a tag needs to be deleted or not. At the end new tags
        # and new taggroups are added.

        # Query latest version of current stakeholder (used to increase version by 1)
        latest_version = self.Session.query(Stakeholder).\
            filter(Stakeholder.stakeholder_identifier == identifier).\
            order_by(desc(Stakeholder.version)).\
            first()

        new_stakeholder = Stakeholder(stakeholder_identifier=db_sh.stakeholder_identifier,
                                      version=(latest_version.version + 1))
        new_stakeholder.tag_groups = []
        # Set the stakeholder status to pending
        new_stakeholder.status = self.Session.query(Status).filter(Status.name == status).first()
        # Add it to the database
        self.Session.add(new_stakeholder)

        # Loop the tag groups from the previous version and copy it to the new
        # version with its tags
        for db_taggroup in self.Session.query(SH_Tag_Group).filter(SH_Tag_Group.fk_stakeholder == db_sh.id):

            # Create a new tag group and add it to the new stakeholder version
            new_taggroup = SH_Tag_Group()
            new_stakeholder.tag_groups.append(new_taggroup)

            # And loop the tags
            for db_tag in self.Session.query(SH_Tag).filter(SH_Tag.fk_sh_tag_group == db_taggroup.id):

                # Before copying the tag, make sure that it is not to delete
                copy_tag = True
                if 'taggroups' in stakeholder_dict:
                    for taggroup_dict in stakeholder_dict['taggroups']:
                        if 'id' in taggroup_dict and taggroup_dict['id'] == db_taggroup.id:
                            # Check which tags we have to edit
                            for tag_dict in taggroup_dict['tags']:
                                if 'id' in tag_dict and tag_dict['id'] == db_tag.id:
                                    # Yes, it is THIS tag
                                    if tag_dict['op'] == 'delete':
                                        copy_tag = False

                # Create and append the new tag only if requested
                if copy_tag:
                    # Get the key and value SQLAlchemy object
                    k = self.Session.query(SH_Key).get(db_tag.fk_key)
                    v = self.Session.query(SH_Value).get(db_tag.fk_value)
                    new_tag = SH_Tag()
                    new_taggroup.tags.append(new_tag)
                    new_tag.key = k
                    new_tag.value = v

                    # Set the main tag
                    if db_taggroup.main_tag == db_tag:
                        new_taggroup.main_tag = new_tag

            # Next step is to add new tags to this tag group without existing ids
            if 'taggroups' in stakeholder_dict:
                for taggroup_dict in stakeholder_dict['taggroups']:
                    if 'id' in taggroup_dict and taggroup_dict['id'] == db_taggroup.id:
                        for tag_dict in taggroup_dict['tags']:
                            if 'id' not in tag_dict and tag_dict['op'] == 'add':
                                new_tag = self._create_tag(request, new_taggroup.tags, tag_dict['key'], tag_dict['value'])
                                # Set the main tag
                                if 'main_tag' in taggroup_dict:
                                    if taggroup_dict['main_tag']['key'] == new_tag.key.key and taggroup_dict['main_tag']['value'] == new_tag.value.value:
                                        new_taggroup.main_tag = new_tag

        # Finally new tag groups (without id) needs to be added
        # (and loop all again)
        if 'taggroups' in stakeholder_dict:
            for taggroup_dict in stakeholder_dict['taggroups']:
                if 'id' not in taggroup_dict and taggroup_dict['op'] == 'add':
                    new_taggroup = SH_Tag_Group()
                    new_stakeholder.tag_groups.append(new_taggroup)
                    for tag_dict in taggroup_dict['tags']:
                        new_tag = self._create_tag(request, new_taggroup.tags, tag_dict['key'], tag_dict['value'])
                        # Set the main tag
                        if 'main_tag' in taggroup_dict:
                            if taggroup_dict['main_tag']['key'] == new_tag.key.key and taggroup_dict['main_tag']['value'] == new_tag.value.value:
                                new_taggroup.main_tag = new_tag

        # Changesets
        self._add_changeset(request, new_stakeholder, old_version)
        
        # Handle involvements
        self._handle_involvements(request, db_sh, new_stakeholder, involvement_change, implicit_inv_change)
        
        return new_stakeholder

    def _create_tag(self, request, parent, key, value):
        """
        Creates a new SQLAlchemy tag object and appends it to the parent list.
        """
        # The key has to be already in the database
        k = self.Session.query(SH_Key).filter(SH_Key.key == key).first()

        # If the value is not yet in the database, create a new value
        v = self.Session.query(SH_Value).filter(SH_Value.value == unicode(value)).first()
        if v is None:
            v = SH_Value(value=value)
            v.fk_language = 1

        # Create a new tag with key and value and append it to the parent tag group
        sh_tag = SH_Tag()
        parent.append(sh_tag)
        sh_tag.key = k
        sh_tag.value = v

        # Return the newly created tag
        return sh_tag

    def _create_stakeholder(self, request, stakeholder, ** kwargs):
        """
        Creates a new stakeholder. As keyword arguments 'identifier' and 'status'
        are allowed.
        """
        identifier = kwargs['identifier'] if 'identifier' in kwargs else uuid.uuid4()
        
        status = 'pending'
        # Get the stakeholder status, default is pending
        if 'status' in kwargs:
            status = kwargs['status']

        # The initial version is 1 of course
        version = 1

        # Create a new stakeholder
        new_stakeholder = Stakeholder(stakeholder_identifier=identifier, version=version)

        new_stakeholder.tag_groups = []
        # Set the stakeholder status
        new_stakeholder.status = self.Session.query(Status).filter(Status.name == status).first()
        # Add it to the database
        self.Session.add(new_stakeholder)

        # Loop all tag groups
        for taggroup in stakeholder['taggroups']:

            db_taggroup = SH_Tag_Group()
            new_stakeholder.tag_groups.append(db_taggroup)

            # Reset the main_tag string
            main_tag = None
            main_tag_key = None
            main_tag_value = None
            # Try to get the main_tag and its key and value from the input JSON
            # file. The main_tag is not mandatory.
            try:
                main_tag = taggroup['main_tag']
                main_tag_key = main_tag['key']
                main_tag_value = main_tag['value']
            except KeyError:
                pass

            # Loop all tags within a tag group
            for tag in taggroup['tags']:

                # Add the tag only if the op property is set to add
                if 'op' not in tag:
                    continue
                elif tag['op'] != 'add':
                    continue

                # Get the key and the value of the current tag
                key = tag['key']
                value = tag['value']

                # Check if the key and value are allowed by the global yaml
                if not self._key_value_is_valid(request, key, value):
                    continue

                # The key has to be already in the database
                k = self.Session.query(SH_Key).filter(SH_Key.key == key).first()

                # If the value is not yet in the database, create a new value
                v = self.Session.query(SH_Value).filter(SH_Value.value == unicode(value)).first()
                if v is None:
                    v = SH_Value(value=value)
                    v.fk_language = 1

                # Create a new tag with key and value and append it to the tag group
                sh_tag = SH_Tag()
                db_taggroup.tags.append(sh_tag)
                sh_tag.key = k
                sh_tag.value = v

                # Check if the current tag is the main tag of this tag group. If
                # yes, set the main_tag attribute to this tag
                if sh_tag.key.key == main_tag_key and sh_tag.value.value == main_tag_value:
                    db_taggroup.main_tag = sh_tag

        self._add_changeset(request, new_stakeholder, None)
        
        return new_stakeholder

    def _add_changeset(self, request, stakeholder, old_version):
        """
        Log the stakeholder change
        """
        # Create a new changeset
        changeset = SH_Changeset(source='[%s] %s' % (stakeholder.status.name, stakeholder.stakeholder_identifier), previous_version=old_version)
        # Get the user from the request
        changeset.user = self.Session.query(User).filter(User.username == request.user.username).first()
        changeset.stakeholder = stakeholder
        self.Session.add(changeset)

    def _key_value_is_valid(self, request, key, value):
        return True

    def read(self, request, filter=None, uid=None):

        # Query the database
        stakeholders, count = self._query(request, limit=self._get_limit(request), offset=self._get_offset(request), filter=filter, uid=uid)

        return {'total': count, 'data': [sh.to_table() for sh in stakeholders]}

    def _query(self, request, limit=None, offset=None, filter=None, uid=None, involvements=None):
        """
        Do the query. Returns
        - a list of (filtered) Activities
        - an Integer with the count of Activities
        """
        from lmkp.views.activity_protocol2 import ActivityProtocol2

        # If no custom filter was provided, get filters from request
        if filter is None:
            # Get the status status
            status_filter = self.Session.query(Status.id).filter(Status.name == self._get_status(request))
            # Get the attribute filter
            tag_filter, filter_length = self._filter(request, SH_Tag, SH_Key, SH_Value)
        
        # Get the order
        order_query, order_numbers = self._get_order(request, Stakeholder, SH_Tag_Group, SH_Tag, SH_Key, SH_Value)

        # Find id's of relevant stakeholders by joining with prepared filters.
        # If result is ordered, do an Outer Join to attach ordered attributes.
        # 'order_value' contains the values to order by.
        if order_query is not None:
            relevant_stakeholders = self.Session.query(
                                                     Stakeholder.id.label('order_id'),
                                                     order_query.c.value.label('order_value')
                                                     ).\
            join(SH_Tag_Group).\
            join(tag_filter, tag_filter.c.filter_tag_id == SH_Tag_Group.id).\
            outerjoin(order_query).\
            group_by(Stakeholder.id, order_query.c.value)
            # order the list (needed to correctly apply limit and offset below)
            if self._get_order_direction(request) == 'DESC':
                if order_numbers:
                    relevant_stakeholders = relevant_stakeholders.order_by(desc(cast(order_query.c.value, Float)))
                else:
                    relevant_stakeholders = relevant_stakeholders.order_by(desc(order_query.c.value))
            else:
                if order_numbers:
                    relevant_stakeholders = relevant_stakeholders.order_by(asc(cast(order_query.c.value, Float)))
                else:
                    relevant_stakeholders = relevant_stakeholders.order_by(asc(order_query.c.value))
        # If result is not ordered, only join with prepared filters is necessary.
        else:
            relevant_stakeholders = self.Session.query(
                                                     Stakeholder.id.label('order_id'),
                                                     func.char_length('').label('order_value') # dummy value
                                                     ).\
            join(SH_Tag_Group).\
            join(tag_filter, tag_filter.c.filter_tag_id == SH_Tag_Group.id).\
            group_by(Stakeholder.id)

        # Apply status filter
        if status_filter:
            relevant_stakeholders = relevant_stakeholders.filter(Stakeholder.fk_status == status_filter)

        # Apply custom filter if one was provided
        if filter:
            relevant_stakeholders = relevant_stakeholders.filter(filter)

        # Apply logical operator
        if self._get_logical_operator(request) == 'or' or filter_length == 0:
            pass
        else:
            # 'AND': all filtered values must be available
            relevant_stakeholders = relevant_stakeholders.having(func.count() >= filter_length)

        # Special case: UID was provided, create new 'relevant_stakeholders'
        if uid is not None:
            relevant_stakeholders = self.Session.query(Stakeholder.id.label('order_id'),
                                                     func.char_length('').label('order_value')).\
                filter(Stakeholder.stakeholder_identifier == uid).\
                filter(Stakeholder.fk_status == status_filter)

        # Count relevant stakeholders (before applying limit and offset)
        count = relevant_stakeholders.count()

        # Apply limit and offset
        relevant_stakeholders = relevant_stakeholders.limit(limit).offset(offset)

        # Prepare query to translate keys and values
        localizer = get_localizer(request)
        lang = None if localizer.locale_name == 'en' \
            else self.Session.query(Language).filter(Language.locale == localizer.locale_name).first()
        key_translation, value_translation = self._get_translatedKV(lang, SH_Key, SH_Value)

        # Prepare query for involvements
        involvement_status = self.Session.query(Activity.id.label("activity_id"),
                                 Activity.activity_identifier.label("activity_identifier")).\
                 filter(Activity.fk_status == status_filter).\
                 subquery()
        involvement_query = self.Session.query(Involvement.fk_stakeholder.label("stakeholder_id"),
                                       Stakeholder_Role.name.label("role_name"),
                                       involvement_status.c.activity_identifier.label("activity_identifier")).\
                   join(involvement_status, involvement_status.c.activity_id == Involvement.fk_activity).\
                   join(Stakeholder_Role).\
                   subquery()

        # Collect all attributes (TagGroups) of relevant stakeholders
        relevant_stakeholders = relevant_stakeholders.subquery()
        query = self.Session.query(Stakeholder.id.label("id"),
                                   Stakeholder.stakeholder_identifier.label("stakeholder_identifier"),
                                   Stakeholder.timestamp.label("timestamp"),
                                   Stakeholder.version.label("version"),
                                   SH_Tag_Group.id.label("taggroup"),
                                   SH_Tag_Group.fk_tag.label("main_tag"),
                                   SH_Tag.id.label("tag"),
                                   SH_Key.key.label("key"),
                                   SH_Value.value.label("value"), \
                                   relevant_stakeholders.c.order_value.label("order_value"),
                                   key_translation.c.key_translated.label("key_translated"),
                                   value_translation.c.value_translated.label("value_translated"),
                                   involvement_query.c.activity_identifier.label("activity_identifier"),
                                   involvement_query.c.role_name.label("stakeholder_role")).\
            join(relevant_stakeholders, relevant_stakeholders.c.order_id == Stakeholder.id).\
            join(SH_Tag_Group).\
            join(SH_Tag, SH_Tag_Group.id == SH_Tag.fk_sh_tag_group).\
            join(SH_Key).\
            join(SH_Value).\
            outerjoin(key_translation, key_translation.c.key_original_id == SH_Key.id).\
            outerjoin(value_translation, value_translation.c.value_original_id == SH_Value.id).\
            outerjoin(involvement_query, involvement_query.c.stakeholder_id == Stakeholder.id)


        # Do the ordering again
        if order_query is not None:
            if self._get_order_direction(request) == 'DESC':
                query = query.order_by(desc(relevant_stakeholders.c.order_value))
            else:
                query = query.order_by(asc(relevant_stakeholders.c.order_value))

        # Put the stakeholders together
        stakeholders = []
        for i in query.all():

            # The stakeholder identifier
            uid = str(i.stakeholder_identifier)

            # The version
            version = i.version

            # The current tag group id (not global unique)
            taggroup_id = int(i.taggroup)

            key = i.key_translated if i.key_translated is not None else i.key
            value = i.value_translated if i.value_translated is not None else i.value

            order_value = i.order_value

            stakeholder = None
            for sh in stakeholders:
                # Use UID to find existing StakeholderFeature or create new one
                if sh.get_guid() == uid:
                    # If list is ordered (order_value != int), use order_value as well
                    # to find existing StakeholderFeature or create new one
                    if not isinstance(order_value, int):
                        if sh.get_order_value() == order_value:
                            stakeholder = sh
                    else:
                        stakeholder = sh

            # If no existing feature found, create new one
            if stakeholder == None:
                stakeholder = Feature(uid, order_value, version=version)
                stakeholders.append(stakeholder)

            # Check if there is already this tag group present in the current
            # stakeholder
            taggroup = None
            if stakeholder.find_taggroup_by_id(taggroup_id) is not None:
                taggroup = stakeholder.find_taggroup_by_id(taggroup_id)
            else:
                taggroup = TagGroup(taggroup_id, i.main_tag)
                stakeholder.add_taggroup(taggroup)

            # Because of Involvements, the same Tags appears for each Involvement, so
            # add it only once to TagGroup
            if taggroup.get_tag_by_id(i.tag) is None:
                taggroup.add_tag(Tag(i.tag, key, value))

            # Determine if and how detailed Involvements are to be displayed
            involvement_details = request.params.get('involvements', None)
            if involvement_details != 'none' and involvements != False:
                # Each Involvement (combination of guid and role) also needs to be added only once
                if i.activity_identifier is not None:
                    if involvement_details == 'full':
                        # Full details, query Activity details
                        if stakeholder.find_involvement_feature(i.activity_identifier, i.stakeholder_role) is None:
                            ap = ActivityProtocol2(self.Session)
                            # Important: involvements=False need to be set, otherwise endless loop occurs
                            activity, count = ap._query(request, uid=i.activity_identifier, involvements=False)
                            stakeholder.add_involvement(Inv(None, activity[0], i.stakeholder_role))
                    else:
                        # Default: only basic information about Involvement
                        if stakeholder.find_involvement(i.activity_identifier, i.stakeholder_role) is None:
                            stakeholder.add_involvement(Inv(i.activity_identifier, None, i.stakeholder_role))

        return stakeholders, count


    def history(self, request, uid, status_list=None):

        # Query the database
        stakeholders, count = self._history(request, uid, status_list, 
            versions=self._get_versions(request))
        
        return {'total': count, 'data': [sh.to_table() for sh in stakeholders]}

    def _history(self, request, uid, status_list=None, versions=None, 
        involvements=None):

        if status_list is None:
            status_list = ['active', 'overwritten', 'deleted']

        status_filter = self.Session.query(Status).\
                            filter(Status.name.in_(status_list)).\
                            subquery()
        
        # Prepare query to translate keys and values
        localizer = get_localizer(request)
        lang = None if localizer.locale_name == 'en' \
            else self.Session.query(Language).filter(Language.locale == localizer.locale_name).first()
        key_translation, value_translation = self._get_translatedKV(lang, SH_Key, SH_Value)    

        # Prepare query for involvements
        involvement_status = self.Session.query(Activity.id.label("activity_id"),
                                 Activity.activity_identifier.label("activity_identifier")).\
                 join(status_filter).\
                 subquery()
        involvement_query = self.Session.query(Involvement.fk_stakeholder.label("stakeholder_id"),
                                       Stakeholder_Role.name.label("role_name"),
                                       involvement_status.c.activity_identifier.label("activity_identifier")).\
                   join(involvement_status, involvement_status.c.activity_id == Involvement.fk_activity).\
                   join(Stakeholder_Role).\
                   subquery()

        query = self.Session.query(Stakeholder.id.label("id"),
                         Stakeholder.stakeholder_identifier.label("stakeholder_identifier"),
                         Stakeholder.timestamp.label("timestamp"),
                         Stakeholder.version.label("version"),
                         SH_Tag_Group.id.label("taggroup"),
                         SH_Tag_Group.fk_tag.label("main_tag"),
                         SH_Tag.id.label("tag"),
                         SH_Key.key.label("key"),
                         SH_Value.value.label("value"),
                         SH_Changeset.previous_version.label("previous_version"),
                         SH_Changeset.source.label("source"),
                         User.id.label("userid"),
                         User.username.label("username"),
                         status_filter.c.name.label("status"),
                         key_translation.c.key_translated.label("key_translated"),
                         value_translation.c.value_translated.label("value_translated"),
                         involvement_query.c.activity_identifier.label("activity_identifier"),
                         involvement_query.c.role_name.label("stakeholder_role")).\
                join(status_filter).\
                join(SH_Changeset).\
                join(User).\
                join(SH_Tag_Group).\
                join(SH_Tag, SH_Tag_Group.id == SH_Tag.fk_tag_group).\
                join(SH_Key).\
                join(SH_Value).\
                outerjoin(key_translation, key_translation.c.key_original_id == SH_Key.id).\
                outerjoin(value_translation, value_translation.c.value_original_id == SH_Value.id).\
                outerjoin(involvement_query, involvement_query.c.stakeholder_id == Stakeholder.id).\
                filter(Stakeholder.stakeholder_identifier == uid).\
                order_by(Stakeholder.version)

        # Append version limit if provided
        if versions is not None:
            query = query.filter(Stakeholder.version.in_(versions))

        # Collect the data from query
        data = []
        for i in query.all():

            # The stakeholder identifier
            uid = str(i.stakeholder_identifier)

            # The current tag group id (not global unique)
            taggroup_id = int(i.taggroup)

            key = i.key_translated if i.key_translated is not None else i.key
            value = i.value_translated if i.value_translated is not None else i.value

            # use version as order value
            order_value = i.version

            diff_info = {
                 'status': i.status,
                 'previous_version': i.previous_version,
                 'userid': i.userid,
                 'username': i.username,
                 'source': i.source
             }

            stakeholder = None
            for a in data:
                # Use order_value (version) to find existing Feature or create new one
                if a.get_order_value() == order_value:
                    stakeholder = a

            # If no existing ActivityFeature found, create new one
            if stakeholder == None:
                stakeholder = Feature(uid, order_value, version=order_value, 
                    diff_info=diff_info)
                data.append(stakeholder)

            # Check if there is already this tag group present in the current
            # stakeholder
            taggroup = None
            if stakeholder.find_taggroup_by_id(taggroup_id) is not None:
                taggroup = stakeholder.find_taggroup_by_id(taggroup_id)
            else:
                taggroup = TagGroup(taggroup_id, i.main_tag)
                stakeholder.add_taggroup(taggroup)

            # Because of Involvements, the same Tags appear for each Involvement, so
            # add it only once to TagGroup
            if taggroup.get_tag_by_id(i.tag) is None:
                taggroup.add_tag(Tag(i.tag, key, value))

            # Determine if and how detailed Involvements are to be displayed
            involvement_details = request.params.get('involvements', None)
            if involvement_details != 'none' and involvements != False:
                # Each Involvement (combination of guid and role) also needs to be added only once
                if i.activity_identifier is not None:
                    if involvement_details == 'full':
                        # Full details, query Activity details
                        if stakeholder.find_involvement_feature(i.activity_identifier, i.stakeholder_role) is None:
                            ap = ActivityProtocol(self.Session)
                            # Important: involvements=False need to be set, otherwise endless loop occurs
                            activity, count = sp._query(request, uid=i.activity_identifier, involvements=False)
                            stakeholder.add_involvement(Inv(None, activity[0], i.stakeholder_role))
                    else:
                        # Default: only basic information about Involvement
                        if stakeholder.find_involvement(i.activity_identifier, i.stakeholder_role) is None:
                            stakeholder.add_involvement(Inv(i.activity_identifier, None, i.stakeholder_role))

        # Loop again through all versions to create diff
        for i, a in enumerate(data):
            if i == 0:
                a.create_diff()
            else:
                a.create_diff(data[i-1])

        return data, len(data)
    
    def _handle_involvements(self, request, old_version, new_version, inv_change, implicit=False):
        """
        Handle the involvements of a Stakeholder.
        - Stakeholder update: copy old involvements
        - Involvement added: copy old involvements, push Activity to new version,
          add new involvement
        - Involvement deleted: copy old involvements (except the one to be removed), 
          push Activity to new version
        - Involvement modified (eg. its role): combination of deleting and adding
          involvements
        """
        from lmkp.views.activity_protocol2 import ActivityProtocol2
        # It is important to keep track of all the Activities where involvements were
        # deleted because they need to be pushed to a new version as well
        awdi_id = [] # = Activities with deleted involvements
        awdi_version = []
        awdi_role = []
        # Copy old involvements if existing
        if old_version is not None:
            for oi in old_version.involvements:
                # Check if involvement is to be removed (op == delete), in which case
                # do not copy it
                remove = False
                if inv_change is not None:
                    for i in inv_change:
                        if ('id' in i and str(i['id']) == str(oi.activity.activity_identifier) and
                            'op' in i and i['op'] == 'delete' and
                            'role' in i and i['role'] == oi.stakeholder_role.id):
                            # Set flag to NOT copy this involvement
                            remove = True
                            # Add identifier and version of Activity to list with
                            # deleted involvements, add them only once
                            if i['id'] not in awdi_id:
                                awdi_id.append(i['id'])
                                awdi_version.append(i['version'])
                                awdi_role.append(i['role'])
                # Also: only copy involvements if status of Activity is 'pending' or 'active'
                if remove is not True and oi.activity.status.id < 3:
                    sh_role = oi.stakeholder_role
                    a = oi.activity
                    # Copy involvement
                    inv = Involvement()
                    inv.stakeholder = new_version
                    inv.activity = a
                    inv.stakeholder_role = sh_role
                    self.Session.add(inv)
        # Add new involvements
        if inv_change is not None:
            for i in inv_change:
                if ('op' in i and i['op'] == 'add' and
                    'id' in i and 'role' in i and 'version' in i):
                    # Query database to find role and previous version of Activity
                    role_db = self.Session.query(Stakeholder_Role).get(i['role'])
                    old_a_db = self.Session.query(Activity).\
                        filter(Activity.activity_identifier == i['id']).\
                        filter(Activity.version == i['version']).\
                        first()
                    if old_a_db is not None:
                        # If the same Activity also has some involvements deleted,
                        # remove it from the list (do not push Activity twice)
                        try:
                            x = awdi_id.index(str(old_a_db.activity_identifier))
                            awdi_id.pop(x)
                            awdi_version.pop(x)
                            awdi_role.pop(x)
                        except ValueError:
                            pass
                        # Push Activity to new version
                        sp = ActivityProtocol2(self.Session)
                        # Simulate a dict
                        a_dict = {'id': old_a_db.activity_identifier, 'version': old_a_db.version}
                        new_a = sp._handle_activity(request, a_dict, 'pending')
                        # Create new inolvement
                        inv = Involvement()
                        inv.stakeholder = new_version
                        inv.activity = new_a
                        inv.stakeholder_role = role_db
                        self.Session.add(inv)
        # Also push Activity where involvements were deleted to new version
        if implicit is not True:
            for i, a in enumerate(awdi_id):
                # Query database
                old_a_db = self.Session.query(Activity).\
                    filter(Activity.activity_identifier == a).\
                    filter(Activity.version == awdi_version[i]).\
                    first()
                # Push Activity to new version
                sp = ActivityProtocol2(self.Session)
                # Simulate a dict
                a_dict = {
                    'id': old_a_db.activity_identifier, 
                    'version': old_a_db.version, 
                    'stakeholders': [{
                        'op': 'delete', 
                        'id': old_version.stakeholder_identifier, 
                        'version': awdi_version[i], 
                        'role': awdi_role[i]
                    }], 
                    'implicit_involvement_update': True
                }
                new_a = sp._handle_activity(request, a_dict, 'pending')