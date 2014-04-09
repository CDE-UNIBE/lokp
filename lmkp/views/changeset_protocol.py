from geoalchemy.functions import functions
from lmkp.models.database_objects import *
from lmkp.views.config import get_current_profile
from lmkp.models.database_objects import *
import logging
from pyramid.httpexceptions import HTTPNotFound
from sqlalchemy.sql import literal_column
from sqlalchemy.sql.expression import desc
from sqlalchemy.sql.expression import or_

log = logging.getLogger(__name__)

class ChangesetProtocol(object):
    """
    
    """

    def __init__(self, Session, ** kwargs):
        self.Session = Session

    def read(self, request):
        """
        
        """
        return {}
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

    def read_many_latest(self, request):

        items = []

        page = int(request.params.get("page", 1))
        pagesize = int(request.params.get("pagesize", 10))

        activities_sub_query = self.Session.query(Activity.activity_identifier.label("identifier"), Activity.version, Changeset.timestamp, Changeset.fk_user).\
            join(Changeset).\
            filter(or_(Activity.fk_status == 2, Activity.fk_status == 3)).\
            filter(self._get_profile_filter(request)).\
            order_by(desc(Changeset.timestamp)).subquery(name="sub_act")

        activities_query = self.Session.query(activities_sub_query, User.username).\
            join(User).order_by(desc(activities_sub_query.c.timestamp)).subquery(name="act")

        # All active and inactive stakeholders
        stakeholder_active = self.Session.query(Stakeholder).\
            filter(or_(Stakeholder.fk_status == 2, Stakeholder.fk_status == 3)).\
            subquery("st_active")

        # Query all stakeholder that have at least one involvement in the current profile
        stakeholder_in_profile = self.Session.query(stakeholder_active).\
            join(Involvement).join(Activity).filter(self._get_profile_filter(request)).\
            distinct().subquery()

        # Get the five latest stakeholder by changeset
        stakeholder_sub_query = self.Session.query(stakeholder_in_profile.c.stakeholder_identifier.label("identifier"), \
                                                   stakeholder_in_profile.c.version, Changeset.timestamp, Changeset.fk_user).\
            join(Changeset, Changeset.id == stakeholder_in_profile.c.fk_changeset).\
            order_by(desc(Changeset.timestamp)).subquery(name="sub_st")

        # Join the resulting set to the user table
        stakeholder_query = self.Session.query(stakeholder_sub_query, User.username).\
            join(User).order_by(desc(stakeholder_sub_query.c.timestamp)).subquery(name="st")

        for i in self.Session.query(activities_query, literal_column("\'activity\'").label("type")).\
            union(self.Session.query(stakeholder_query, literal_column("\'stakeholder\'").label("type"))).\
            order_by(desc(activities_query.c.timestamp)).\
            order_by(desc(activities_query.c.version)).\
            offset((page-1)*pagesize).limit(pagesize).all():
            formatted_timestamp = i.timestamp.strftime("%a, %d %b %Y %H:%M:%S")
            short_uuid = str(i.identifier).split("-")[0].upper()
            if i.type == 'activity':
                activity_link = request.route_url("activities_read_one", output="html", uid=i.identifier, _query={"v": i.version})
                description_text = """
                Deal <a href=\"%s\">#%s</a> has been updated by user
                <a href=\"%s\">%s</a> on %s to version&nbsp;%s
                """ % (activity_link,\
                        short_uuid,\
                        request.route_url("changesets_read_byuser", username=i.username, output="html"),\
                        i.username,\
                        formatted_timestamp,\
                        i.version),
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
                description_text = """
                Investor <a href=\"%s\">#%s</a> has been updated by user
                <a href=\"%s\">%s</a> on %s to version&nbsp;%s
                """ % (stakeholder_link,\
                        short_uuid,\
                        request.route_url("changesets_read_byuser", username=i.username, output="html"),\
                        i.username,\
                        formatted_timestamp,\
                        i.version),
                items.append({
                             "title":  "Investor %s updated to version %s" % (short_uuid, i.version),
                             "description": unicode(description_text[0]),
                             "link": stakeholder_link,
                             "author": i.username,
                             "guid": "%s?v=%s" % (i.identifier, i.version),
                             "pubDate": formatted_timestamp
                             })
        return {
            "link": request.route_url("changesets_read_latest", output="rss"),
            "image": {
                "url": '/custom/img/logo.png',
                "title": "landobservatory.org",
                "link": request.route_url("index")
            },
            "items": items
        }

    def read_many_byuser(self, request):

        username = request.matchdict['username']

        page = int(request.params.get("page", 1))
        pagesize = int(request.params.get("pagesize", 10))

        if self.Session.query(User).filter(User.username == username).first() == None:
            raise HTTPNotFound("Requested user does not exist.")

        items = []

        max_limit = 25

        activities_sub_query = self.Session.query(Activity.activity_identifier.label("identifier"), Activity.version, Changeset.timestamp, Changeset.fk_user).\
            join(Changeset).\
            filter(or_(Activity.fk_status == 2, Activity.fk_status == 3)).subquery(name="sub_act")

        activities_query = self.Session.query(activities_sub_query, User.username).\
            join(User).filter(User.username == username).subquery(name="act")

        # All active and inactive stakeholders
        stakeholder_active = self.Session.query(Stakeholder).\
            filter(or_(Stakeholder.fk_status == 2, Stakeholder.fk_status == 3)).\
            subquery("st_active")

        # Get the five latest stakeholder by changeset
        stakeholder_sub_query = self.Session.query(stakeholder_active.c.stakeholder_identifier.label("identifier"), \
                                                   stakeholder_active.c.version, Changeset.timestamp, Changeset.fk_user).\
            join(Changeset, Changeset.id == stakeholder_active.c.fk_changeset).\
            subquery(name="sub_st")

        # Join the resulting set to the user table
        stakeholder_query = self.Session.query(stakeholder_sub_query, User.username).\
            join(User).filter(User.username == username).subquery(name="st")

        for i in self.Session.query(activities_query, literal_column("\'activity\'").label("type")).\
            union(self.Session.query(stakeholder_query, literal_column("\'stakeholder\'").label("type"))).\
            order_by(desc(activities_query.c.timestamp)).\
            order_by(desc(activities_query.c.version)).\
            offset((page-1)*pagesize).limit(pagesize).all():
            formatted_timestamp = i.timestamp.strftime("%a, %d %b %Y %H:%M:%S")
            short_uuid = str(i.identifier).split("-")[0].upper()
            if i.type == 'activity':
                activity_link = request.route_url("activities_read_one", output="html", uid=i.identifier, _query={"v": i.version})
                description_text = "Update of deal <a href=\"%s\">#%s</a> on %s to version&nbsp;%s" \
                    % (activity_link, short_uuid, formatted_timestamp, i.version),
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
                description_text = "Update of investor <a href=\"%s\">#%s</a> on %s to version&nbsp;%s" \
                    % (stakeholder_link, short_uuid, formatted_timestamp, i.version),
                items.append({
                             "title":  "Investor %s updated to version %s" % (short_uuid, i.version),
                             "description": unicode(description_text[0]),
                             "link": stakeholder_link,
                             "author": i.username,
                             "guid": "%s?v=%s" % (i.identifier, i.version),
                             "pubDate": formatted_timestamp
                             })
        return {
            "link": request.route_url("changesets_read_latest", output="rss"),
            "image": {
                "url": '/custom/img/logo.png',
                "title": "landobservatory.org",
                "link": request.route_url("index")
            },
            "items": items,
            "username": username
        }

        return {}

    def _get_profile_filter(self, request):
        """
            Return a spatial filter based on the profile boundary of the current
            profile which is queried from the database.
            Copied from the ActivityProtocol3
            """

        profile = self.Session.query(Profile).\
            filter(Profile.code == get_current_profile(request)).\
            first()

        if profile is None:
            return (Activity.id == 0)

        return functions.intersects(
                                    Activity.point, profile.geometry
                                    )

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