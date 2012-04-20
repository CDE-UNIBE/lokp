from lmkp.models.database_objects import *
from sqlalchemy.sql.expression import or_

class ActivityProtocol2(object):

    def __init__(self, Session):

        self.Session = Session

    def read(self, request, filter=None, uid=None):
        return self._query(request, filter)


    def _query(self, request, filter=None):
        """
        Build a query based on the filter and the request params,
        and send the query to the database.

        Returns a set of tuples with the following attributes:
        id | activity_identifier | geometry | timestamp | version | key | value

        """

        # Check if a timestamp is set
        if request.params.get('timestamp', None) is not None:
            return self._query_timestamp(request, filter).all()

        # Create the query
#        query = self.Session.query(Activity.id.label("id"),
#                                   Activity.activity_identifier.label("activity_identifier"),
#                                   Activity.point.label("geometry"),
#                                   Activity.timestamp.label("timestamp"),
#                                   Activity.version.label("version"),
#                                   A_Tag_Group.id.label("taggroup"),
#                                   A_Key.key.label("key"),
#                                   A_Value.value.label("value")
#                                   ).join(A_Tag_Group).join(A_Tag).join(A_Key).join(A_Value).join(Status).group_by(Activity.id, A_Tag_Group.id, A_Key.key, A_Value.value).order_by(Activity.id).filter(filter)

        query = self.Session.query(Activity.id.label("id"),
                                   Activity.activity_identifier.label("activity_identifier"),
                                   Activity.point.label("geometry"),
                                   Activity.timestamp.label("timestamp"),
                                   Activity.version.label("version"),
                                   A_Tag_Group.id.label("taggroup"),
                                   A_Tag.id.label("tag"),
                                   A_Key.key.label("key"),
                                   A_Value.value.label("value")
                                   ).join(A_Tag_Group).join(A_Tag).join(A_Key).join(A_Value).filter(or_(Activity.id == 50, Activity.id == 51))
                                 
        activities = []
        for i in query.all():

            # The activity identifier
            uid = str(i[1])

            # The current tag group id (not global unique)
            taggroup_id = int(i[5])

            key = i[7]
            value = i[8]
            
            activity = None
            for a in activities:
                if a['id'] == uid:
                    activity = a
                    
            if activity == None:
                activity = {'id': uid}
                activities.append(activity)

            # Append a list of tag groups if not yet present
            if 'taggroups' not in activity:
                activity['taggroups'] = []

            # Check if there is already this tag group present in the current
            # activity
            taggroup = None
            for t in activity['taggroups']:
                if t['id'] == taggroup_id:
                    taggroup = t

            if taggroup == None:
                taggroup = {'id': taggroup_id}
                activity['taggroups'].append(taggroup)

            taggroup[key] = value


        return activities


        