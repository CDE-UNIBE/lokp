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
        a_changesetsJoins = self.Session.query(A_Changeset.source, Activity.activity_identifier.label("activity"), User.username, Status.name).join(A_Changeset.user).join(A_Changeset.activity).join(Status)

        # filters first
        a_changesetsJoins = a_changesetsJoins.filter(self._filter_user(request)).filter(self._filter_status(request))

        # Create a list of activity changesets
        activities = []
        for i in a_changesetsJoins.limit(self._limit_changesets(request)).offset(self._offset_changesets(request)):
            activities.append({'source': i[0], 'activity': str(i[1]), 'user': i[2], 'status': i[3]})
        #activities.append({'total': a_changesetsJoins.count()})

        # Join the stakeholder changesets with the stakeholders and the users
        sh_changesetsJoins = self.Session.query(SH_Changeset.source, Stakeholder.stakeholder_identifier.label("stakeholder"), User.username, Status.name).join(SH_Changeset.user).join(SH_Changeset.stakeholder).join(Status)

        # Create a list of stakeholder changesets
        stakeholders = []
        for i in sh_changesetsJoins.filter(self._filter_user(request)).filter(self._filter_status(request)).limit(self._limit_changesets(request)):
            stakeholders.append({'source': i[0], 'stakeholder': str(i[1]), 'user': i[2], 'status': i[3]})

        return {'activities': activities, 'activities_count': a_changesetsJoins.count(), 'stakeholders': stakeholders}

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