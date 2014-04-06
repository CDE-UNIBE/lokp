from lmkp.models.database_objects import *
import logging
from lmkp.models.database_objects import *
from sqlalchemy.sql import literal_column
from sqlalchemy.sql.expression import column
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql.expression import or_
from sqlalchemy.sql.expression import select
from sqlalchemy.sql.expression import union

log = logging.getLogger(__name__)

class ChangesetProtocol(object):
    """
    
    """

    def __init__(self, Session, ** kwargs):
        self.Session = Session

    def read(self, request):
        """
        
        """

        #TODO: Revamp this!
        # 2013/02/05: Commented everything to prevent error message.

#        # Join the activity changesets with the activities and the users
#        a_changesetsJoins = self.Session.query(A_Changeset.source, Activity.activity_identifier.label("activity"), User.username, Status.name).join(A_Changeset.user).join(A_Changeset.activity).join(Status)
#
#        # filters first
#        a_changesetsJoins = a_changesetsJoins.filter(self._filter_user(request)).filter(self._filter_status(request))
#
#        # Create a list of activity changesets
#        activities = []
#        for i in a_changesetsJoins.limit(self._limit_changesets(request)).offset(self._offset_changesets(request)):
#            activities.append({'source': i[0], 'activity': str(i[1]), 'user': i[2], 'status': i[3]})
#        #activities.append({'total': a_changesetsJoins.count()})
#
#        # Join the stakeholder changesets with the stakeholders and the users
#        sh_changesetsJoins = self.Session.query(SH_Changeset.source, Stakeholder.stakeholder_identifier.label("stakeholder"), User.username, Status.name).join(SH_Changeset.user).join(SH_Changeset.stakeholder).join(Status)
#
#        # Create a list of stakeholder changesets
#        stakeholders = []
#        for i in sh_changesetsJoins.filter(self._filter_user(request)).filter(self._filter_status(request)).limit(self._limit_changesets(request)):
#            stakeholders.append({'source': i[0], 'stakeholder': str(i[1]), 'user': i[2], 'status': i[3]})
#
#        return {'activities': activities, 'activities_count': a_changesetsJoins.count(), 'stakeholders': stakeholders}

        return {}

    def read_many_latest(self, request):

        items = []

        max_limit = 5

        activities_sub_query = self.Session.query(Activity.activity_identifier.label("identifier"), Activity.version, Changeset.timestamp, Changeset.fk_user).\
            join(Changeset).\
            filter(or_(Activity.fk_status == 2, Activity.fk_status == 3)).\
            order_by(desc(Changeset.timestamp)).limit(max_limit).subquery(name="sub_act")

        activities_query = self.Session.query(activities_sub_query, User.username).\
            join(User).order_by(desc(activities_sub_query.c.timestamp)).subquery(name="act")

        stakeholder_sub_query = self.Session.query(Stakeholder.stakeholder_identifier.label("identifier"), Stakeholder.version, Changeset.timestamp, Changeset.fk_user).\
            join(Changeset).\
            filter(or_(Stakeholder.fk_status == 2, Stakeholder.fk_status == 3)).\
            order_by(desc(Changeset.timestamp)).limit(max_limit).subquery(name="sub_st")

        stakeholder_query = self.Session.query(stakeholder_sub_query, User.username).\
            join(User).order_by(desc(stakeholder_sub_query.c.timestamp)).subquery(name="st")

        for i in self.Session.query(activities_query, literal_column("\'activity\'").label("type")).\
            union(self.Session.query(stakeholder_query, literal_column("\'stakeholder\'").label("type"))).\
            order_by(desc(activities_query.c.timestamp)).all():
            formatted_timestamp = i.timestamp.strftime("%a, %w %b %Y %H:%M:%S")
            short_uuid = str(i.identifier).split("-")[0]
            if i.type == 'activity':
                activity_link = request.route_url("activities_read_one", output="html", uid=i.identifier, _query={"v": i.version})
                description_text = "Activity <a href=\"%s\">%s</a> has been updated by user \"%s\" on %s to version %s" \
                    % (activity_link, short_uuid, i.username, formatted_timestamp, i.version),
                items.append({
                             "title":  "Activity %s updated to version %s" % (short_uuid, i.version),
                             "description": unicode(description_text[0]),
                             "link": activity_link,
                             "author": i.username,
                             "guid": "%s?v=%s" % (i.identifier, i.version),
                             "pubDate": formatted_timestamp
                             })
            elif i.type == 'stakeholder':
                stakeholder_link = request.route_url("stakeholders_read_one", output="html", uid=i.identifier, _query={"v": i.version})
                description_text = "Investor <a href=\"%s\">%s</a> has been updated by user \"%s\" on %s to version %s" \
                    % (stakeholder_link, short_uuid, i.username, formatted_timestamp, i.version),
                items.append({
                             "title":  "Investor %s updated to version %s" % (short_uuid, i.version),
                             "description": unicode(description_text[0]),
                             "link": stakeholder_link,
                             "author": i.username,
                             "guid": "%s?v=%s" % (i.identifier, i.version),
                             "pubDate": formatted_timestamp
                             })
        return {
            "title": "Latest changes on the Landobservatory",
            "link": request.route_url("changesets_read_latest", output="rss"),
            "description": "Shows the latest changes on the Landobservatory",
            "image": {
                "url": '/custom/img/logo.png',
                "title": "landobservatory.org",
                "link": request.route_url("index")
            },
            "items": items
        }

    def _filter_user(self, request):
        """
                    Returns a filter with the requested user or None
                    """
        user = request.params.get('user', None)
        if user is not None:
            return User.username == user

        return None

    def _filter_status(self, request):
        """
                    Returns a filter with the requested status or None
                    """
        status = request.params.get('status', None)
        if status is not None:
            return Status.name == status

    def _limit_changesets(self, request):
        """
                    Returns a limit or None
                    """

        limit = request.params.get('limit', None)
        if limit is not None:
            try:
                return int(limit)
            except ValueError:
                pass

        return None

    def _offset_changesets(self, request):

        offset = request.params.get('offset', None)
        if offset is not None:
            try:
                return int(offset)
            except ValueError:
                pass

        return None