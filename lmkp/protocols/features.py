import datetime
from shapely import wkb

from lmkp.views.translation import get_translated_status


class Feature(object):

    def __init__(self, guid, order_value, version=None, status=None,
                 status_id=None, timestamp=None, diff_info=None, ** kwargs):
        self._taggroups = []
        self._involvements = []
        self._guid = guid
        self._order_value = order_value
        self._version = version
        self._timestamp = timestamp
        self._diff_info = diff_info
        self._status = status
        self._status_id = status_id
        self._pending = []
        self._missing_keys = None

        self._previous_version = kwargs.pop('previous_version', None)

        self._user_privacy = kwargs.pop('user_privacy', None)
        self._user_id = kwargs.pop('user_id', None)
        self._user_name = kwargs.pop('user_name', None)
        self._user_firstname = kwargs.pop('user_firstname', None)
        self._user_lastname = kwargs.pop('user_lastname', None)

        self._institution_id = kwargs.pop('institution_id', None)
        self._institution_name = kwargs.pop('institution_name', None)
        self._institution_url = kwargs.pop('institution_url', None)
        self._institution_logo = kwargs.pop('institution_logo', None)

    def add_taggroup(self, taggroup):
        """
        Adds a new tag group to the internal tag group list
        """
        self._taggroups.append(taggroup)

    def add_involvement(self, involvement):
        self._involvements.append(involvement)

    def remove_involvement(self, involvement):
        self._involvements.remove(involvement)

    def find_involvement_by_guid(self, guid):
        for i in self._involvements:
            if (str(i.get_guid()) == str(guid)):
                return i
        return None

    def find_involvement_by_role(self, guid, role):
        for i in self._involvements:
            if (str(i.get_guid()) == str(guid) and i.get_role() == role):
                return i
        return None

    def find_involvement(self, guid, role, version):
        for i in self._involvements:
            if (str(i.get_guid()) == str(guid) and i.get_role() == role and
                    i.get_version() == version):
                return i
        return None

    def find_involvement_feature(self, guid, role):
        for i in self._involvements:
            if i._feature._guid == str(guid) and i.get_role() == role:
                return i
        return None

    def find_taggroup_by_id(self, id):
        for t in self._taggroups:
            if t.get_id() == id:
                return t
        return None

    def find_taggroup_by_tg_id(self, tg_id):
        for t in self._taggroups:
            if t.get_tg_id() == tg_id:
                return t
        return None

    def get_taggroups(self):
        return self._taggroups

    def get_involvements(self):
        return self._involvements

    def get_version(self):
        return self._version

    def get_status(self):
        return self._status

    def get_status_id(self):
        return self._status_id

    def get_guid(self):
        return self._guid

    def set_pending(self, pending):
        self._pending = pending

    def remove_taggroup(self, taggroup):
        if taggroup in self.get_taggroups():
            self.get_taggroups().remove(taggroup)

    def get_metadata(self, request):
        """
        Return a dict with some metadata
        """
        return {
            'version': self._version,
            'status': get_translated_status(request, self._status),
            'statusId': self._status_id,
            'timestamp': datetime.datetime.strftime(
                self._timestamp, '%Y-%m-%d %H:%M:%S'),
            'username': self._user_name,
        }

    def mark_complete(self, mandatory_keys):
        """
        Return a list of missing mandatory keys. Return [0] if item is to be
        deleted
        """

        # Make a copy of mandatory keys
        mk = mandatory_keys[:]

        for k in mandatory_keys:
            for tg in self.get_taggroups():
                if tg.get_tag_by_key(k) is not None:
                    mk.remove(k)
                    break

        # If all mandatory keys are still there, check if version is pending to
        # be deleted
        if len(mk) == len(mandatory_keys):
            if len(self.get_taggroups()) == 0:
                mk = []

        self._missing_keys = mk

    def to_table(self, request):
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

        ret = {'id': self._guid, 'taggroups': tg}

        if geometry is not None:
            ret['geometry'] = geometry

        if self._version is not None:
            ret['version'] = self._version
        if self._timestamp is not None:
            ret['timestamp'] = str(self._timestamp)
        if self._status is not None:
            ret['status'] = get_translated_status(request, self._status)
        if self._status_id is not None:
            ret['status_id'] = self._status_id
        if self._diff_info is not None:
            for k in self._diff_info:
                # Try to translate status
                if k == 'status':
                    ret[k] = get_translated_status(request, self._diff_info[k])
                else:
                    ret[k] = self._diff_info[k]
        if len(self._pending) != 0:
            pending = []
            for p in self._pending:
                pending.append(p.to_table(request))
            ret['pending'] = sorted(
                pending, key=lambda k: k['version'], reverse=True)
        if self._missing_keys is not None:
            ret['missing_keys'] = self._missing_keys

        # Involvements
        if len(self._involvements) != 0:
            sh = []
            for i in self._involvements:
                sh.append(i.to_table(request))
            ret['involvements'] = sh

        if self._previous_version is not None:
            ret['previous_version'] = self._previous_version

        # User details
        user = {}
        if self._user_id is not None:
            user['id'] = self._user_id
        if self._user_name is not None:
            user['username'] = self._user_name
        # User details based on privacy settings
        if self._user_privacy is not None and self._user_privacy > 0:
            if self._user_firstname is not None:
                user['firstname'] = self._user_firstname
            if self._user_lastname is not None:
                user['lastname'] = self._user_lastname
        if user != {}:
            ret['user'] = user

        # Institutions
        institution = {}
        if self._institution_id is not None:
            institution['id'] = self._institution_id
        if self._institution_name is not None:
            institution['name'] = self._institution_name
        if self._institution_url is not None:
            institution['url'] = self._institution_url
        if self._institution_logo is not None:
            institution['logo'] = self._institution_logo
        if institution != {}:
            ret['institution'] = institution

        return ret

    def create_diff(self, request, previous=None):
        """
        Append a diff object. Try to find TagGroups and Tags of current version
        in previous version.
        Also find new or removed Involvements.
        """

        if previous is not None:
            # Collect new TagGroups
            diff_new = []
            # Loop through TagGroups of current version
            for tg in self._taggroups:
                # Special case: Item was deleted, then the taggroup has only
                # one empty tag: Do not mark this as new attribute.
                if (len(tg.get_tags()) == 1
                    and tg.get_tags()[0].get_key() is None
                        and tg.get_tags()[0].get_value() is None):
                    pass
                else:
                    # Indicator (None, False or TagGroup) to check if all Tags
                    # were found in the same TagGroup
                    foundinsametaggroup = None
                    # Loop through Tags of current version
                    for t in tg.get_tags():
                        # Indicator (True or False) to flag if a Tag was found
                        # in the previous version
                        newtag_found = False
                        # Variable to store the old TagGroup where a Tag was
                        # found
                        foundintaggroup = None
                        # Try to find the same Tag in previous version by
                        # looping through TagGroups of previous version
                        for tg_old in previous.get_taggroups():
                            # Only look at old TagGroups that were not yet
                            # found
                            if tg_old.getDiffFlag() is not True:
                                # Loop through Tags of previous version
                                for t_old in tg_old.get_tags():
                                    # Compare Key and Value of current and
                                    # previous Tag
                                    if (t.get_key() == t_old.get_key()
                                        and t.get_value()
                                            == t_old.get_value()):
                                        # Tag is found in previous version,
                                        # set indicator and store TagGroup
                                        newtag_found = True
                                        foundintaggroup = tg_old
                                        break

                        # Tag was found in old Tags
                        if newtag_found is True:
                            # For the first tag of a TagGroup, store the old
                            # TagGroup
                            if foundinsametaggroup is None:
                                foundinsametaggroup = foundintaggroup
                            # Check if the found Tag is not in the same
                            # TagGroup as the others
                            elif foundintaggroup != foundinsametaggroup:
                                foundinsametaggroup = False
                        # Tag was not found after looping through all old Tags
                        else:
                            foundinsametaggroup = False

                    # All Tags were in the same TagGroup
                    if foundinsametaggroup is not False:
                        if foundinsametaggroup is not None:
                            # Mark old TagGroup as found
                            foundinsametaggroup.setDiffFlag(True)
                    # Else, TagGroup is new
                    else:
                        diff_new.append(tg.to_table())

            # Collect old TagGroups that are not there anymore
            diff_old = []
            for tg_old in previous.get_taggroups():
                if tg_old.getDiffFlag() is not True:
                    diff_old.append(tg_old.to_table())

            # Reset all TagGroups to compare with next version
            for tg in self._taggroups:
                tg.setDiffFlag(None)
            # Also reset TagGroups of previous version
            for tg in previous._taggroups:
                tg.setDiffFlag(None)

            # Collect new Involvements
            inv_new = []
            # Loop through Involvements of current version
            for invn in self._involvements:
                newinv_found = False
                for invo in previous._involvements:
                    if (invn.get_guid() == invo.get_guid() and
                            invn.get_role() == invo.get_role()):
                        newinv_found = True
                        break
                if newinv_found is not True:
                    inv_new.append(invn.to_table(request))

            # Collect old Involvements (not there anymore)
            inv_old = []
            # Loop through Involvements of previous version
            for invo in previous._involvements:
                oldinv_found = False
                for invn in self._involvements:
                    if (invo.get_guid() == invn.get_guid() and
                            invo.get_role() == invn.get_role()):
                        oldinv_found = True
                        break
                if oldinv_found is not True:
                    inv_old.append(invo.to_table(request))

            # Put it all together
            diff_object = {}
            if len(diff_new) > 0:
                diff_object['new_attr'] = diff_new
            if len(diff_old) > 0:
                diff_object['old_attr'] = diff_old
            if len(inv_old) > 0:
                diff_object['old_inv'] = inv_old
            if len(inv_new) > 0:
                diff_object['new_inv'] = inv_new

            # Only add diff object if not empty
            if diff_object != {}:
                self._diff_info['diff'] = diff_object

    def get_order_value(self):
        return self._order_value

    def get_previous_version(self):
        return self._previous_version
