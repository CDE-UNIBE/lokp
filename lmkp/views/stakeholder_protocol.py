from lmkp.models.database_objects import SH_Changeset
from lmkp.models.database_objects import SH_Key
from lmkp.models.database_objects import SH_Tag
from lmkp.models.database_objects import SH_Tag_Group
from lmkp.models.database_objects import SH_Value
from lmkp.models.database_objects import Stakeholder
from lmkp.models.database_objects import Status
from lmkp.models.database_objects import User
from lmkp.views.protocol import Feature
from lmkp.views.protocol import Protocol
from lmkp.views.protocol import Tag
from lmkp.views.protocol import TagGroup
import logging
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPCreated
from pyramid.i18n import get_localizer
from sqlalchemy import func
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

        for stakeholder in raw['stakeholders']:
            self._handle_stakeholder(request, stakeholder)

        # Return the newly created object with 201 Created HTTP code status
        return HTTPCreated(detail='Ok')

    def _handle_stakeholder(self, request, stakeholder_dict, status='pending'):

        # If this stakeholder does not have an id then create a new stakeholder
        if 'id' not in stakeholder_dict:
            self._create_stakeholder(request, stakeholder_dict, status=status)
            return

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
            self._create_stakeholder(request, stakeholder_dict, identifier=identifier, status=status)
            return

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
                    k = self.Session.query(SH_Key).get(db_tag.fk_sh_key)
                    v = self.Session.query(SH_Value).get(db_tag.fk_sh_value)
                    new_tag = SH_Tag()
                    new_taggroup.tags.append(new_tag)
                    new_tag.key = k
                    new_tag.value = v

                    # Set the main tag
                    if db_taggroup.main_tag == db_tag:
                        new_taggroup.main_tag = new_tag

            # Next step is to add new tags to this tag group without existing ids
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
        for taggroup_dict in stakeholder_dict['taggroups']:
            if taggroup_dict['id'] is None and taggroup_dict['op'] == 'add':
                new_taggroup = SH_Tag_Group()
                new_stakeholder.tag_groups.append(new_taggroup)
                for tag_dict in taggroup_dict['tags']:
                    new_tag = self._create_tag(request, new_taggroup.tags, tag_dict['key'], tag_dict['value'])
                    # Set the main tag
                    if 'main_tag' in taggroup_dict:
                        if taggroup_dict['main_tag']['key'] == new_tag.key.key and taggroup_dict['main_tag']['value'] == new_tag.value.value:
                            new_taggroup.main_tag = new_tag

        self._add_changeset(request, new_stakeholder, old_version)

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

        identifier = None
        if 'identifier' in kwargs:
            identifier = kwargs['identifier']
        status = 'pending'
        # Get the stakeholder status, default is pending
        if 'status' in kwargs:
            status = kwargs['status']

        # Create a new unique identifier if not set
        if identifier is None:
            identifier = uuid.uuid4()
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

    def _add_changeset(self, request, stakeholder, old_version):
        """
        Log the stakeholder change
        """
        # Create a new changeset
        changeset = SH_Changeset(source='[%s] %s' % (stakeholder.status.name, stakeholder), previous_version=old_version)
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

    def _query(self, request, limit=None, offset=None, filter=None, uid=None):
        """
        Do the query. Returns
        - a list of (filtered) Activities
        - an Integer with the count of Activities
        """

        # If no custom filter was provided, get filters from request
        if filter is None:
            # Get the status status
            status_filter = self.Session.query(Status.id).filter(Status.name == self._get_status(request))
            # Get the attribute filter
            tag_filter, filter_length = self._filter(request, SH_Tag, SH_Key, SH_Value)
        
        # Get the order
        order_query, order_numbers = self._get_order(request)

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
                filter(Stakeholder.stakeholder_identifier == uid)

        # Count relevant stakeholders (before applying limit and offset)
        count = relevant_stakeholders.count()

        # Apply limit and offset
        relevant_stakeholders = relevant_stakeholders.limit(limit).offset(offset)

        # Prepare query to translate keys and values
        localizer = get_localizer(request)
        lang = None if localizer.locale_name == 'en' \
            else self.Session.query(Language).filter(Language.locale == localizer.locale_name).first()
        key_translation, value_translation = self._get_translatedKV(lang)

        # Collect all attributes (TagGroups) of relevant stakeholders
        relevant_stakeholders = relevant_stakeholders.subquery()
        query = self.Session.query(Stakeholder.id.label("id"),
                                   Stakeholder.stakeholder_identifier.label("stakeholder_identifier"),
                                   Stakeholder.timestamp.label("timestamp"),
                                   Stakeholder.version.label("version"),
                                   SH_Tag_Group.id.label("taggroup"),
                                   SH_Tag_Group.fk_sh_tag.label("main_tag"),
                                   SH_Tag.id.label("tag"),
                                   SH_Key.key.label("key"),
                                   SH_Value.value.label("value"), \
                                   relevant_stakeholders.c.order_value.label("order_value"),
                                   key_translation.c.key_translated.label("key_translated"),
                                   value_translation.c.value_translated.label("value_translated")).\
            join(relevant_stakeholders, relevant_stakeholders.c.order_id == Stakeholder.id).\
            join(SH_Tag_Group).\
            join(SH_Tag, SH_Tag_Group.id == SH_Tag.fk_sh_tag_group).\
            join(SH_Key).\
            join(SH_Value).\
            outerjoin(key_translation, key_translation.c.key_original_id == SH_Key.id).\
            outerjoin(value_translation, value_translation.c.value_original_id == SH_Value.id)


        # Do the ordering again
        if order_query is not None:
            if self._get_order_direction(request) == 'DESC':
                query = query.order_by(desc(relevant_stakeholders.c.order_value))
            else:
                query = query.order_by(asc(relevant_stakeholders.c.order_value))

        # Put the stakeholders together
        stakeholders = []
        for i in query.all():

            # The activity identifier
            uid = str(i[1])

            # The version
            version = i[3]

            # The current tag group id (not global unique)
            taggroup_id = int(i[4])

            key = i[10] if i[10] is not None else i[7]
            value = i[11] if i[11] is not None else i[8]

            order_value = i[9]

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

            # If no existing StakeholderFeature found, create new one
            if stakeholder == None:
                stakeholder = StakeholderFeature(uid, order_value, version=version)
                stakeholders.append(stakeholder)

            # Check if there is already this tag group present in the current
            # activity
            taggroup = None
            if stakeholder.find_taggroup_by_id(taggroup_id) is not None:
                taggroup = stakeholder.find_taggroup_by_id(taggroup_id)
            else:
                taggroup = TagGroup(taggroup_id, i[5])
                stakeholder.add_taggroup(taggroup)

            taggroup.add_tag(Tag(i[6], key, value))

        return stakeholders, count

    def _get_order(self, request):
        """
        Returns
        - a SubQuery with an ordered list of Activity IDs and
          the values by which they will be ordered.
        - a Boolean indicating order values are numbers or not
        """
        order_key = request.params.get('order_by', None)
        if order_key is not None:
            # Query to order number values (cast to Float)
            q_number = self.Session.query(
                Stakeholder.id,
                cast(SH_Value.value, Float).label('value')).\
            join(SH_Tag_Group).\
            join(SH_Tag, SH_Tag.fk_sh_tag_group == SH_Tag_Group.id).\
            join(SH_Value).\
            join(SH_Key).\
            filter(SH_Key.key.like(order_key))
            # Query to order string values
            q_text = self.Session.query(
                Stakeholder.id,
                SH_Value.value.label('value')).\
            join(SH_Tag_Group).\
            join(SH_Tag, SH_Tag.fk_sh_tag_group == SH_Tag_Group.id).\
            join(SH_Value).\
            join(SH_Key).\
            filter(SH_Key.key.like(order_key))

            # Try to query numbered values and cast them
            try:
                x = q_number.all()
                return q_number.subquery(), True
            except:
                # Rolling back of Session is needed to completely erase error thrown above
                self.Session.rollback()
                return q_text.subquery(), False

        return None, None

    def _get_translatedKV(self, lang):
        """
        Returns
        - a SubQuery with a list of all translated keys
        - a SubQuery with a list of all translated values
        """
        key_query = self.Session.query(SH_Key.fk_sh_key.label("key_original_id"),
                                SH_Key.key.label("key_translated")).\
                    filter(SH_Key.language == lang).\
                    subquery()
        value_query = self.Session.query(SH_Value.fk_sh_value.label("value_original_id"),
                                 SH_Value.value.label("value_translated")).\
                     filter(SH_Value.language == lang).\
                     subquery()
        return key_query, value_query


class StakeholderFeature(Feature):

    def __init__(self, guid, order_value, version=None, diff_info=None, ** kwargs):
        self._taggroups = []
        self._guid = guid
        self._order_value = order_value
        self._version = version
        self._diff_info = diff_info
        