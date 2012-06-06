from geoalchemy import WKBSpatialElement
from geoalchemy.functions import functions
from lmkp.config import config_file_path
from lmkp.models.database_objects import *
import logging
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.httpexceptions import HTTPCreated
from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import HTTPNotFound
from shapely.geometry import asShape
from shapely.geometry.polygon import Polygon
import simplejson as json
from sqlalchemy import alias
from sqlalchemy import join
from sqlalchemy import select
from sqlalchemy import distinct
from sqlalchemy import func
from sqlalchemy.orm.util import AliasedClass
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql.expression import asc
from sqlalchemy.sql.expression import or_
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import Float
import yaml
from pyramid.i18n import get_localizer

log = logging.getLogger(__name__)

class Tag(object):

    def __init__(self, id, key, value):
        self._id = id
        self._key = key
        self._value = value

    def get_key(self):
        return self._key

    def get_value(self):
        return self._value

    def get_id(self):
        return self._id

    def to_table(self):
        return {'id': self._id, 'key': self._key, 'value': self._value}

class TagGroup(object):
    
    def __init__(self, id=None, main_tag_id=None):
        """
        Create a new TagGroup object with id and the main_tag_id
        """

        # The TagGroup id
        self._id = id
        # The id of the main tag (not the tag itself!)
        self._main_tag_id = main_tag_id
        # List to store the tags
        self._tags = []

    def add_tag(self, tag):
        """
        Add a new tag to the internal tag list
        """
        self._tags.append(tag)

    def get_id(self):
        return self._id

    def get_tag_by_key(self, key):
        """
        Returns a tag from this group if there is one with the requested key,
        else None is returned.
        """
        for t in self._tags:
            if t.get_key() == key:
                return t

        return None

    def to_table(self):
        """
        Returns a JSON compatible representation of this object
        """
        main_tag = None
        tags = []
        for t in self._tags:
            tags.append(t.to_table())
            if t.get_id() == self._main_tag_id:
                main_tag = t.to_table()

        return {'id': self._id, 'main_tag': main_tag, 'tags': tags}

class ActivityFeature2(object):

    def __init__(self, guid, order_value, geometry=None, status=None, version=None, ** kwargs):
        self._taggroups = []
        self._guid = guid
        self._order_value = order_value
        self._geometry = geometry
        self._status = status
        self._version = version

    def add_taggroup(self, taggroup):
        """
        Adds a new tag group to the internal tag group list
        """
        self._taggroups.append(taggroup)

    def find_taggroup_by_id(self, id):
        for t in self._taggroups:
            if t.get_id() == id:
                return t
        
        return None

    def to_table(self):
        """
        Returns a JSON compatible representation of this object
        """
        tg = []
        for t in self._taggroups:
            tg.append(t.to_table())

        geometry = None

        try:
            geom = wkb.loads(str(self._geometry.geom_wkb))
            geometry = {}
            geometry['type'] = 'Point'
            geometry['coordinates'] = [geom.x, geom.y]
        except AttributeError:
            pass

        ret = {'id': self._guid, 'taggroups': tg, 'geometry': geometry}

        if self._status is not None:
            ret['status'] = self._status
        if self._version is not None:
            ret['version'] = self._version
        
        return ret

    def get_guid(self):
        return self._guid
    
    def get_order_value(self):
        return self._order_value


class ActivityProtocol2(object):

    def __init__(self, Session):

        self.Session = Session

    def read(self, request, filter=None, uid=None):

        # Query the database
        activities, count = self._query(request, limit=self._get_limit(request), offset=self._get_offset(request), filter=filter, uid=uid)

        return {'total': count, 'data': [a.to_table() for a in activities]}

    def history(self, request, uid, status_list=None):
        
        # Query the database
        activities, count = self._history(request, uid, status_list)
        
        return {'total': count, 'data': [a.to_table() for a in activities]}

    def create(self, request):
        """
        Add or update activities
        """
        
        raw = request.json_body

        # Check if the json body is a valid diff file
        #if 'create' not in raw and 'modify' not in raw and 'delete' not in raw:
        if 'activities' not in raw:
            return HTTPBadRequest(detail="Not a valid format")

        for activity in raw['activities']:
            self._handle_activity(request, activity)

        # Return the newly created object with 201 Created HTTP code status
        return HTTPCreated(detail="ok")

    def _handle_activity(self, request, activity_dict, status='pending'):
        """
        """

        # If this activity does not have an id then create a new activity
        if 'id' not in activity_dict:
            self._create_activity(request, activity_dict, status=status)
            return

        # Get the identifier from the request
        identifier = activity_dict['id']
        old_version = activity_dict['version'] if 'version' in activity_dict else None

        # Try to get the activity from the database with this id
        db_a = self.Session.query(Activity).\
            filter(Activity.activity_identifier == identifier).\
            filter(Activity.version == old_version).\
            first()

        # If no activity is found, create a new activity
        if db_a == None:
            self._create_activity(request, activity_dict, identifier=identifier, status=status)
            return
        
        # Update the activity:
        # The basic idea is to deep copy the previous version and control during
        # the copying if a tag needs to be deleted or not. At the end new tags
        # and new taggroups are added.
        
        # Query latest version of current activity (used to increase version by 1)
        latest_version = self.Session.query(Activity).\
            filter(Activity.activity_identifier == identifier).\
            order_by(desc(Activity.version)).\
            first()
            
        new_activity = Activity(activity_identifier=db_a.activity_identifier,
                                version=(latest_version.version + 1),
                                point=db_a.point)
        new_activity.tag_groups = []
        # Set the activity status to pending
        new_activity.status = self.Session.query(Status).filter(Status.name == status).first()
        # Add it to the database
        self.Session.add(new_activity)

        # Loop the tag groups from the previous version and copy it to the new
        # version with its tags
        for db_taggroup in self.Session.query(A_Tag_Group).filter(A_Tag_Group.fk_activity == db_a.id):

            # Create a new tag group and add it to the new activity version
            new_taggroup = A_Tag_Group()
            new_activity.tag_groups.append(new_taggroup)

            # And loop the tags
            for db_tag in self.Session.query(A_Tag).filter(A_Tag.fk_a_tag_group == db_taggroup.id):

                # Before copying the tag, make sure that it is not to delete
                copy_tag = True
                for taggroup_dict in activity_dict['taggroups']:
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
                    k = self.Session.query(A_Key).get(db_tag.fk_a_key)
                    v = self.Session.query(A_Value).get(db_tag.fk_a_value)
                    new_tag = A_Tag()
                    new_taggroup.tags.append(new_tag)
                    new_tag.key = k
                    new_tag.value = v

                    # Set the main tag
                    if db_taggroup.main_tag == db_tag:
                        new_taggroup.main_tag = new_tag

            # Next step is to add new tags to this tag group without existing ids
            for taggroup_dict in activity_dict['taggroups']:
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
        for taggroup_dict in activity_dict['taggroups']:
            if taggroup_dict['id'] is None and taggroup_dict['op'] == 'add':
                new_taggroup = A_Tag_Group()
                new_activity.tag_groups.append(new_taggroup)
                for tag_dict in taggroup_dict['tags']:
                    new_tag = self._create_tag(request, new_taggroup.tags, tag_dict['key'], tag_dict['value'])
                    # Set the main tag
                    if 'main_tag' in taggroup_dict:
                        if taggroup_dict['main_tag']['key'] == new_tag.key.key and taggroup_dict['main_tag']['value'] == new_tag.value.value:
                            new_taggroup.main_tag = new_tag

        self._add_changeset(request, new_activity, old_version)

    def _create_tag(self, request, parent, key, value):
        """
        Creates a new SQLAlchemy tag object and appends it to the parent list.
        """
        # The key has to be already in the database
        k = self.Session.query(A_Key).filter(A_Key.key == key).first()

        # If the value is not yet in the database, create a new value
        v = self.Session.query(A_Value).filter(A_Value.value == unicode(value)).first()
        if v is None:
            v = A_Value(value=value)
            v.fk_language = 1

        # Create a new tag with key and value and append it to the parent tag group
        a_tag = A_Tag()
        parent.append(a_tag)
        a_tag.key = k
        a_tag.value = v

        # Return the newly created tag
        return a_tag

    def _create_activity(self, request, activity, ** kwargs):
        """
        Creates a new activity. As keyword arguments 'identifier' and 'status'
        are allowed.
        """

        if 'identifier' in kwargs:
            identifier = kwargs['identifier']
        status = 'pending'
        if 'status' in kwargs:
            status = kwargs['status']

        # Create a new unique identifier if not set
        if identifier is None:
            identifier = uuid.uuid4()
        # The initial version is 1 of course
        version = 1

        # Try to get the geometry
        try:
            geom = geojson.loads(json.dumps(activity['geometry']),
                                 object_hook=geojson.GeoJSON.to_instance)

            # The geometry
            shape = asShape(geom)
            # Create a new activity and add a representative point to the activity
            new_activity = Activity(activity_identifier=identifier, version=version, point=shape.representative_point().wkt)
        except KeyError:
            # If no geometry is submitted, create a new activity without a geometry
            new_activity = Activity(activity_identifier=identifier, version=version)

        new_activity.tag_groups = []
        # Set the activity status to pending
        new_activity.status = self.Session.query(Status).filter(Status.name == status).first()
        # Add it to the database
        self.Session.add(new_activity)

        # Loop all tag groups
        for taggroup in activity['taggroups']:

            db_taggroup = A_Tag_Group()
            new_activity.tag_groups.append(db_taggroup)

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
                k = self.Session.query(A_Key).filter(A_Key.key == key).first()

                # If the value is not yet in the database, create a new value
                v = self.Session.query(A_Value).filter(A_Value.value == unicode(value)).first()
                if v is None:
                    v = A_Value(value=value)
                    v.fk_language = 1

                # Create a new tag with key and value and append it to the tag group
                a_tag = A_Tag()
                db_taggroup.tags.append(a_tag)
                a_tag.key = k
                a_tag.value = v

                # Check if the current tag is the main tag of this tag group. If
                # yes, set the main_tag attribute to this tag
                if a_tag.key.key == main_tag_key and a_tag.value.value == main_tag_value:
                    db_taggroup.main_tag = a_tag

        self._add_changeset(request, new_activity)

    def _add_changeset(self, request, activity, old_version):
        """
        Log the activity
        """
        # Create a new changeset
        changeset = A_Changeset(source='[%s] %s' % (activity.status.name, activity), previous_version=old_version)
        # Get the user from the request
        changeset.user = self.Session.query(User).filter(User.username == request.user.username).first()
        changeset.activity = activity
        self.Session.add(changeset)

    def _filter(self, request):
        """
        Returns
        - a SubQuery of Tags containing a union of all Key/Value pairs which fulfill
          the filter condition(s)
        - a count of the filters
        """

        def __get_filter_expression(value, op):
            
            # Use cast function provided by SQLAlchemy to convert
            # database values to Float.
            nbr_map = {
                'eq': cast(A_Value.value, Float) == value,
                'ne': cast(A_Value.value, Float) != value,
                'lt': cast(A_Value.value, Float) < value,
                'lte': cast(A_Value.value, Float) <= value,
                'gt': cast(A_Value.value, Float) > value,
                'gte': cast(A_Value.value, Float) >= value
            }
    
            str_map = {
                'like': A_Value.value.like(value),
                'ilike': A_Value.value.ilike(value)
            }
            
            # number comparison
            if op in nbr_map.keys():
                # make sure submitted value is a number
                try:
                    float(value)
                    return nbr_map[op]
                except:
                    pass
            
            elif op in str_map.keys():
                return str_map[op]
            
            return None

        if 'queryable' in request.params:
            filter_expr = []
            for k in request.params:
                # Collect filter expressions
                if len(request.params[k]) <= 0 or '__' not in k:
                    continue
                col, op = k.split('__')
                # Several values can be queried for one attributes e.g.
                # project_use equals pending and signed. Build the URL
                # like: queryable=project_use&project_use__eq=pending,signed
                values = request.params[k].split(',')
                for v in values:
                    q = self.Session.query(A_Tag.id.label('filter_tag_id')).\
                        join(A_Key).\
                        join(A_Value).\
                        filter(A_Key.key == col).\
                        filter(__get_filter_expression(v, op))
                    filter_expr.append(q)

            # Do a union of all filter expressions and return it
            if len(filter_expr) > 0:
                tag = filter_expr[0].union(*filter_expr[1:])
                return tag.subquery(), len(filter_expr)

        # Default (no filtering)
        return self.Session.query(A_Tag.id.label("filter_tag_id")).subquery(), 0

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
            tag_filter, filter_length = self._filter(request)
        
        # Get the order
        order_query, order_numbers = self._get_order(request)
        
        # Find id's of relevant activities by joining with prepared filters.
        # If result is ordered, do an Outer Join to attach ordered attributes.
        # 'order_value' contains the values to order by.
        if order_query is not None:
            relevant_activities = self.Session.query(
                Activity.id.label('order_id'),
                order_query.c.value.label('order_value')
            ).\
            join(A_Tag_Group).\
            join(tag_filter, tag_filter.c.filter_tag_id == A_Tag_Group.id).\
            outerjoin(order_query).\
            group_by(Activity.id, order_query.c.value)
            # order the list (needed to correctly apply limit and offset below)
            if self._get_order_direction(request) == 'DESC':
                if order_numbers:
                    relevant_activities = relevant_activities.order_by(desc(cast(order_query.c.value, Float)))
                else:
                    relevant_activities = relevant_activities.order_by(desc(order_query.c.value))
            else:
                if order_numbers:
                    relevant_activities = relevant_activities.order_by(asc(cast(order_query.c.value, Float)))
                else:
                    relevant_activities = relevant_activities.order_by(asc(order_query.c.value))
        # If result is not ordered, only join with prepared filters is necessary.
        else:
            relevant_activities = self.Session.query(
                Activity.id.label('order_id'),
                func.char_length('').label('order_value') # dummy value
            ).\
            join(A_Tag_Group).\
            join(tag_filter, tag_filter.c.filter_tag_id == A_Tag_Group.id).\
            group_by(Activity.id)

        # Apply status filter
        if status_filter:
            relevant_activities = relevant_activities.filter(Activity.fk_status == status_filter)
        
        # Apply custom filter if one was provided
        if filter:
            relevant_activities = relevant_activities.filter(filter)
        
        # Apply logical operator
        if self._get_logical_operator(request) == 'or' or filter_length == 0:
            pass
        else:
            # 'AND': all filtered values must be available
            relevant_activities = relevant_activities.having(func.count() >= filter_length)

        # Special case: UID was provided, create new 'relevant_activities'
        if uid is not None:
            relevant_activities = self.Session.query(Activity.id.label('order_id'),
                                                     func.char_length('').label('order_value')).\
                                                     filter(Activity.activity_identifier == uid)

        # Count relevant activities (before applying limit and offset)
        count = relevant_activities.count()
        
        # Apply limit and offset
        relevant_activities = relevant_activities.limit(limit).offset(offset)

        # Prepare query to translate keys and values
        localizer = get_localizer(request)
        lang = None if localizer.locale_name == 'en' \
                else self.Session.query(Language).filter(Language.locale == localizer.locale_name).first()
        key_translation, value_translation = self._get_translatedKV(lang)

        # Collect all attributes (TagGroups) of relevant activities
        relevant_activities = relevant_activities.subquery()
        query = self.Session.query(Activity.id.label("id"),
                         Activity.activity_identifier.label("activity_identifier"),
                         Activity.point.label("geometry"),
                         Activity.timestamp.label("timestamp"),
                         Activity.version.label("version"),
                         A_Tag_Group.id.label("taggroup"),
                         A_Tag_Group.fk_a_tag.label("main_tag"),
                         A_Tag.id.label("tag"),
                         A_Key.key.label("key"),
                         A_Value.value.label("value"),\
                         relevant_activities.c.order_value.label("order_value"),
                         key_translation.c.key_translated.label("key_translated"),
                         value_translation.c.value_translated.label("value_translated")).\
            join(relevant_activities, relevant_activities.c.order_id == Activity.id).\
            join(A_Tag_Group).\
            join(A_Tag, A_Tag_Group.id == A_Tag.fk_a_tag_group).\
            join(A_Key).\
            join(A_Value).\
            outerjoin(key_translation, key_translation.c.key_original_id == A_Key.id).\
            outerjoin(value_translation, value_translation.c.value_original_id == A_Value.id)
        
        
        # Do the ordering again
        if order_query is not None:
            if self._get_order_direction(request) == 'DESC':
                query = query.order_by(desc(relevant_activities.c.order_value))
            else:
                query = query.order_by(asc(relevant_activities.c.order_value))

        # Put the activities together
        activities = []
        for i in query.all():

            # The activity identifier
            uid = str(i[1])

            # The geometry
            g = i[2]

            # The version
            version = i[4]

            # The current tag group id (not global unique)
            taggroup_id = int(i[5])

            key = i[11] if i[11] is not None else i[8]
            value = i[12] if i[12] is not None else i[9]

            order_value = i[10]
            
            activity = None
            for a in activities:
                # Use UID to find existing ActivityFeature or create new one
                if a.get_guid() == uid:
                    # If list is ordered (order_value != int), use order_value as well
                    # to find existing ActivityFeature or create new one
                    if not isinstance(order_value, int):
                        if a.get_order_value() == order_value:
                            activity = a
                    else:
                        activity = a

            # If no existing ActivityFeature found, create new one
            if activity == None:
                activity = ActivityFeature2(uid, order_value, geometry=g, version=version)
                activities.append(activity)

            # Check if there is already this tag group present in the current
            # activity
            taggroup = None
            if activity.find_taggroup_by_id(taggroup_id) is not None:
                taggroup = activity.find_taggroup_by_id(taggroup_id)
            else:
                taggroup = TagGroup(taggroup_id, i[6])
                activity.add_taggroup(taggroup)

            taggroup.add_tag(Tag(i[7], key, value))

        return activities, count

    def _history(self, request, uid, status_list=None):
        
        if status_list is None:
            status_list = ['active', 'overwritten', 'deleted']
        
        status_filter = self.Session.query(Status).\
                            filter(Status.name.in_(status_list)).\
                            subquery()

        query = self.Session.query(Activity.id.label("id"),
                         Activity.activity_identifier.label("activity_identifier"),
                         Activity.point.label("geometry"),
                         Activity.timestamp.label("timestamp"),
                         Activity.version.label("version"),
                         A_Tag_Group.id.label("taggroup"),
                         A_Tag_Group.fk_a_tag.label("main_tag"),
                         A_Tag.id.label("tag"),
                         A_Key.key.label("key"),
                         A_Value.value.label("value"),
                         status_filter.c.name.label("status")).\
                join(status_filter).\
                join(A_Tag_Group).\
                join(A_Tag, A_Tag_Group.id == A_Tag.fk_a_tag_group).\
                join(A_Key).\
                join(A_Value).\
                filter(Activity.activity_identifier == uid).\
                order_by(Activity.version)
        
        # Collect the data from query
        data = []
        for i in query.all():
            
            # The activity identifier
            uid = str(i[1])

            # The geometry
            g = i[2]

            # The current tag group id (not global unique)
            taggroup_id = int(i[5])

            key = i[8]
            value = i[9]

            # use version as order value
            order_value = i[4]
            
            status = i[10]
            
            activity = None
            for a in data:
                # Use order_value (version) to find existing ActivityFeature or create new one
                if a.get_order_value() == order_value:
                    activity = a
            
            # If no existing ActivityFeature found, create new one
            if activity == None:
                activity = ActivityFeature2(uid, order_value, geometry=g, status=status)
                data.append(activity)
            
            # Check if there is already this tag group present in the current
            # activity
            taggroup = None
            if activity.find_taggroup_by_id(taggroup_id) is not None:
                taggroup = activity.find_taggroup_by_id(taggroup_id)
            else:
                taggroup = TagGroup(taggroup_id, i[6])
                activity.add_taggroup(taggroup)

            taggroup.add_tag(Tag(i[7], key, value))
        
        return data, len(data)

    def _create_geom_filter(self, request):
        """
            """

        try:
            epsg = int(request.params.get('epsg', 4326))
        except:
            epsg = 4326

        bbox = request.params.get('bbox', None)
        if bbox is not None:
            box = map(float, bbox.split(','))
            geometry = Polygon((
                               (box[0], box[1]),
                               (box[0], box[3]),
                               (box[2], box[3]),
                               (box[2], box[1]),
                               (box[0], box[1]))
                               )

            wkb_geometry = WKBSpatialElement(buffer(geometry.wkb), epsg)

            return functions.intersects(Activity.point, wkb_geometry)

        return None


    def _get_limit(self, request):

        limit = request.params.get('limit', None)
        if limit is not None:
            try:
                return int(limit)
            except ValueError:
                pass

        return None

    def _get_status(self, request):
        """
        Returns the requested activity status, default value is active.
        """

        status = request.params.get('status', None)
        # Hard coded list of possible activity statii. Not very nice ... But more
        # performant than requesting the database
        if status in ["pending", "active", "overwritten", "deleted", "rejected"]:
            return status

        return "active"

    def _get_offset(self, request):
        """
        Returns the requested offset, default value is 0
        """
        offset = request.params.get('offset', 0)
        try:
            return int(offset)
        except ValueError:
            pass

        return 0

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
                Activity.id, 
                cast(A_Value.value, Float).label('value')).\
            join(A_Tag_Group).\
            join(A_Tag, A_Tag.fk_a_tag_group == A_Tag_Group.id).\
            join(A_Value).\
            join(A_Key).\
            filter(A_Key.key.like(order_key))
            # Query to order string values
            q_text = self.Session.query(
                Activity.id, 
                A_Value.value.label('value')).\
            join(A_Tag_Group).\
            join(A_Tag, A_Tag.fk_a_tag_group == A_Tag_Group.id).\
            join(A_Value).\
            join(A_Key).\
            filter(A_Key.key.like(order_key))
            
            # Try to query numbered values and cast them
            try:
                x = q_number.all()
                return q_number.subquery(), True
            except:
                # Rolling back of Session is needed to completely erase error thrown above
                self.Session.rollback()
                return q_text.subquery(), False

        return None, None

    def _get_order_direction(self, request):
        """
        Return the direction of ordering only if it is set to DESC
        """
        if request.params.get('dir', '').upper() == 'DESC':
            return 'DESC'

    def _get_logical_operator(self, request):
        """
        Return the logical operator if set, default is 'and'
        """
        return request.params.get("logical_op", "and").lower()

    def _get_translatedKV(self, lang):
        """
        Returns
        - a SubQuery with a list of all translated keys
        - a SubQuery with a list of all translated values
        """
        key_query = self.Session.query(A_Key.fk_a_key.label("key_original_id"),
                                A_Key.key.label("key_translated")).\
                    filter(A_Key.language == lang).\
                    subquery()
        value_query = self.Session.query(A_Value.fk_a_value.label("value_original_id"),
                                 A_Value.value.label("value_translated")).\
                     filter(A_Value.language == lang).\
                     subquery()
        return key_query, value_query

    def _key_value_is_valid(self, request, key, value):
        # Read the global configuration file
        global_stream = open(config_file_path(request), 'r')
        global_config = yaml.load(global_stream)

        log.debug(global_config)

        return True

