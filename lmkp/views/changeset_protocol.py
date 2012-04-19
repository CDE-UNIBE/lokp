from lmkp.models.database_objects import *
import logging

log = logging.getLogger(__name__)

class ChangesetProtocol(object):
    """
    
    """

    def __init__(self, Session, ** kwargs):
        self.Session = Session

    def read(self, request):
        """
        
        """

        # Join the activity changesets with the activities and the users
        a_changesetsJoins = self.Session.query(A_Changeset.source, Activity.activity_identifier.label("activity"), User.username).join(A_Changeset.user).join(A_Changeset.activity)

        # Create a list of activity changesets
        activities = []
        for i in a_changesetsJoins.filter(self._filter_user(request)).limit(self._limit_changesets(request)):
            activities.append({'source': i[0], 'activity': str(i[1]), 'user': i[2]})

        # Join the stakeholder changesets with the stakeholders and the users
        sh_changesetsJoins = self.Session.query(SH_Changeset.source, Stakeholder.stakeholder_identifier.label("stakeholder"), User.username).join(SH_Changeset.user).join(SH_Changeset.stakeholder)

        # Create a list of stakeholder changesets
        stakeholders = []
        for i in sh_changesetsJoins.filter(self._filter_user(request)).limit(self._limit_changesets(request)):
            stakeholders.append({'source': i[0], 'stakeholder': str(i[1]), 'user': i[2]})

        return {'activities': activities, 'stakeholders': stakeholders}

    def _filter_user(self, request):
        """
        Returns a filter with the requested user or None
        """
        user = request.params.get('user', None)
        if user is not None:
            return User.username == user

        return None

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