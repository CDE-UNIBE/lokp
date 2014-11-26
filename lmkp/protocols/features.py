import datetime
from shapely import wkb
from shapely import geometry

from lmkp.protocols.protocol import get_status_name_by_id


class ItemFeature(object):
    """
    TODO
    """

    def __init__(self, identifier, order_value, version, status_id):

        self._identifier = identifier
        self._version = version
        self._order_value = order_value
        self._status_id = status_id

        self._taggroups = []
        self._involvements = []

        self._status = None
        self._timestamp = None
        self._previous_version = None

        self._userid = None
        self._username = None
        self._user_privacy = None
        self._user_firstname = None
        self._user_lastname = None
        self._institution_id = None
        self._institution_name = None
        self._institution_url = None
        self._institution_logo = None

        self._diff_info = None
        self._pending = []
        self._missing_keys = None

    @property
    def identifier(self):
        return self._identifier

    @property
    def version(self):
        return self._version

    @property
    def order_value(self):
        return self._order_value

    @property
    def status_id(self):
        return self._status_id

    @property
    def timestamp(self):
        return self._timestamp

    @timestamp.setter
    def timestamp(self, value):
        self._timestamp = value

    @property
    def previous_version(self):
        return self._previous_version

    @previous_version.setter
    def previous_version(self, value):
        self._previous_version = value

    @property
    def userid(self):
        return self._userid

    @userid.setter
    def userid(self, value):
        self._userid = value

    @property
    def username(self):
        return self._username

    @username.setter
    def username(self, value):
        self._username = value

    @property
    def user_privacy(self):
        return self._user_privacy

    @user_privacy.setter
    def user_privacy(self, value):
        self._user_privacy = value

    @property
    def user_firstname(self):
        return self._user_firstname

    @user_firstname.setter
    def user_firstname(self, value):
        self._user_firstname = value

    @property
    def user_lastname(self):
        return self._user_lastname

    @user_lastname.setter
    def user_lastname(self, value):
        self._user_lastname = value

    @property
    def institution_id(self):
        return self._institution_id

    @institution_id.setter
    def institution_id(self, value):
        self._institution_id = value

    @property
    def institution_name(self):
        return self._institution_name

    @institution_name.setter
    def institution_name(self, value):
        self._institution_name = value

    @property
    def institution_url(self):
        return self._institution_url

    @institution_url.setter
    def institution_url(self, value):
        self._institution_url = value

    @property
    def institution_logo(self):
        return self._institution_logo

    @institution_logo.setter
    def institution_logo(self, value):
        self._institution_logo = value

    @property
    def taggroups(self):
        return self._taggroups

    def add_taggroup(self, taggroup):
        """
        Add a new taggroup to the internal Taggroup list. It is only
        added if it is a :class:`ItemTaggroup` object.

        Args:
            ``taggroup`` (:class:`ItemTaggroup`): A
            :class:`ItemTaggroup` object.
        """
        if isinstance(taggroup, ItemTaggroup):
            self.taggroups.append(taggroup)

    def get_taggroup_by_id(self, id):
        """
        Return a Taggroup based on its id.

        Args:
            ``id`` (int): The id of the Taggroup to be returned.

        Returns:
            :class:`ItemTaggroup` or ``None``. The Taggroup or None if
            no Taggroup with the given id was found.
        """
        for t in self.taggroups:
            if t.id == id:
                return t
        return None

    @property
    def involvements(self):
        return self._involvements

    def add_involvement(self, inv):
        """
        TODO
        """
        self.involvements.append(inv)

    # def remove_involvement(self, involvement):
    #     self._involvements.remove(involvement)

    # def find_involvement_by_guid(self, guid):
    #     for i in self._involvements:
    #         if (str(i.get_guid()) == str(guid)):
    #             return i
    #     return None

    # def find_involvement_by_role(self, guid, role):
    #     for i in self._involvements:
    #         if (str(i.get_guid()) == str(guid) and i.get_role() == role):
    #             return i
    #     return None

    # def find_involvement(self, guid, role, version):
    #     for i in self._involvements:
    #         if (str(i.get_guid()) == str(guid) and i.get_role() == role and
    #                 i.get_version() == version):
    #             return i
    #     return None

    # def find_involvement_feature(self, guid, role):
    #     for i in self._involvements:
    #         if i._feature._guid == str(guid) and i.get_role() == role:
    #             return i
    #     return None

    # def find_taggroup_by_tg_id(self, tg_id):
    #     for t in self._taggroups:
    #         if t.get_tg_id() == tg_id:
    #             return t
    #     return None

    # def get_taggroups(self):
    #     return self._taggroups

    # def get_involvements(self):
    #     return self._involvements

    # # def get_version(self):
    # #     return self._version

    # def get_status(self):
    #     return self._status

    # def get_status_id(self):
    #     return self._status_id

    # # def get_guid(self):
    # #     return self._guid

    # def set_pending(self, pending):
    #     self._pending = pending

    # def remove_taggroup(self, taggroup):
    #     if taggroup in self.get_taggroups():
    #         self.get_taggroups().remove(taggroup)

    # def get_metadata(self, request):
    #     """
    #     Return a dict with some metadata
    #     """
    #     return {
    #         'version': self._version,
    #         'status': get_translated_status(request, self._status),
    #         'statusId': self._status_id,
    #         'timestamp': datetime.datetime.strftime(
    #             self._timestamp, '%Y-%m-%d %H:%M:%S'),
    #         'username': self._username,
    #     }

    # def mark_complete(self, mandatory_keys):
    #     """
    #     Return a list of missing mandatory keys. Return [0] if item is to be
    #     deleted
    #     """

    #     # Make a copy of mandatory keys
    #     mk = mandatory_keys[:]

    #     for k in mandatory_keys:
    #         for tg in self.get_taggroups():
    #             if tg.get_tag_by_key(k) is not None:
    #                 mk.remove(k)
    #                 break

    #     # If all mandatory keys are still there, check if version is pending to
    #     # be deleted
    #     if len(mk) == len(mandatory_keys):
    #         if len(self.get_taggroups()) == 0:
    #             mk = []

    #     self._missing_keys = mk

    def to_json(self, request):
        """
        Return a JSON compatible representation of the Feature and its
        Taggroups.

        Args:
            ``request`` (pyramid.request): A :term:`Pyramid` Request
            object.

        Returns:
            ``dict``. A dict containing the id, Taggroups, status and
            version details and information about the user and
            institution if available.
        """
        ret = {
            'id': self.identifier,
            'status_id': self.status_id,
            'version': self.version,
            'taggroups': [tg.to_json() for tg in self.taggroups],
            'timestamp': (
                str(self.timestamp) if self.timestamp is not None else None),
            'status': get_status_name_by_id(self.status_id, request),
            'previous_version': self.previous_version
        }

        # if self._diff_info is not None:
        #     for k in self._diff_info:
        #         # Try to translate status
        #         if k == 'status':
        #             ret[k] = get_translated_status(request, self._diff_info[k])
        #         else:
        #             ret[k] = self._diff_info[k]
        # if len(self._pending) != 0:
        #     pending = []
        #     for p in self._pending:
        #         pending.append(p.to_table(request))
        #     ret['pending'] = sorted(
        #         pending, key=lambda k: k['version'], reverse=True)
        # if self._missing_keys is not None:
        #     ret['missing_keys'] = self._missing_keys

        # Involvements
        if len(self.involvements) > 0:
            ret['involvements'] = [
                i.to_json(request) for i in self.involvements]

        # User details
        if self.userid is not None and self.username is not None:
            user_details = {
                'id': self.userid,
                'username': self.username
            }
            # Details based on privacy settings
            if self.user_privacy > 0:
                user_details.update({
                    'firstname': self.user_firstname,
                    'lastname': self.user_lastname
                })
            ret['user'] = user_details

        # Institutions
        if (self.institution_id is not None
                and self.institution_name is not None):
            ret['institution'] = {
                'id': self.institution_id,
                'name': self.institution_name,
                'url': self.institution_url,
                'logo': self.institution_logo
            }

        return ret

    # def create_diff(self, request, previous=None):
    #     """
    #     Append a diff object. Try to find TagGroups and Tags of current version
    #     in previous version.
    #     Also find new or removed Involvements.
    #     """

    #     if previous is not None:
    #         # Collect new TagGroups
    #         diff_new = []
    #         # Loop through TagGroups of current version
    #         for tg in self._taggroups:
    #             # Special case: Item was deleted, then the taggroup has only
    #             # one empty tag: Do not mark this as new attribute.
    #             if (len(tg.get_tags()) == 1
    #                 and tg.get_tags()[0].get_key() is None
    #                     and tg.get_tags()[0].get_value() is None):
    #                 pass
    #             else:
    #                 # Indicator (None, False or TagGroup) to check if all Tags
    #                 # were found in the same TagGroup
    #                 foundinsametaggroup = None
    #                 # Loop through Tags of current version
    #                 for t in tg.get_tags():
    #                     # Indicator (True or False) to flag if a Tag was found
    #                     # in the previous version
    #                     newtag_found = False
    #                     # Variable to store the old TagGroup where a Tag was
    #                     # found
    #                     foundintaggroup = None
    #                     # Try to find the same Tag in previous version by
    #                     # looping through TagGroups of previous version
    #                     for tg_old in previous.get_taggroups():
    #                         # Only look at old TagGroups that were not yet
    #                         # found
    #                         if tg_old.getDiffFlag() is not True:
    #                             # Loop through Tags of previous version
    #                             for t_old in tg_old.get_tags():
    #                                 # Compare Key and Value of current and
    #                                 # previous Tag
    #                                 if (t.get_key() == t_old.get_key()
    #                                     and t.get_value()
    #                                         == t_old.get_value()):
    #                                     # Tag is found in previous version,
    #                                     # set indicator and store TagGroup
    #                                     newtag_found = True
    #                                     foundintaggroup = tg_old
    #                                     break

    #                     # Tag was found in old Tags
    #                     if newtag_found is True:
    #                         # For the first tag of a TagGroup, store the old
    #                         # TagGroup
    #                         if foundinsametaggroup is None:
    #                             foundinsametaggroup = foundintaggroup
    #                         # Check if the found Tag is not in the same
    #                         # TagGroup as the others
    #                         elif foundintaggroup != foundinsametaggroup:
    #                             foundinsametaggroup = False
    #                     # Tag was not found after looping through all old Tags
    #                     else:
    #                         foundinsametaggroup = False

    #                 # All Tags were in the same TagGroup
    #                 if foundinsametaggroup is not False:
    #                     if foundinsametaggroup is not None:
    #                         # Mark old TagGroup as found
    #                         foundinsametaggroup.setDiffFlag(True)
    #                 # Else, TagGroup is new
    #                 else:
    #                     diff_new.append(tg.to_table())

    #         # Collect old TagGroups that are not there anymore
    #         diff_old = []
    #         for tg_old in previous.get_taggroups():
    #             if tg_old.getDiffFlag() is not True:
    #                 diff_old.append(tg_old.to_table())

    #         # Reset all TagGroups to compare with next version
    #         for tg in self._taggroups:
    #             tg.setDiffFlag(None)
    #         # Also reset TagGroups of previous version
    #         for tg in previous._taggroups:
    #             tg.setDiffFlag(None)

    #         # Collect new Involvements
    #         inv_new = []
    #         # Loop through Involvements of current version
    #         for invn in self._involvements:
    #             newinv_found = False
    #             for invo in previous._involvements:
    #                 if (invn.get_guid() == invo.get_guid() and
    #                         invn.get_role() == invo.get_role()):
    #                     newinv_found = True
    #                     break
    #             if newinv_found is not True:
    #                 inv_new.append(invn.to_table(request))

    #         # Collect old Involvements (not there anymore)
    #         inv_old = []
    #         # Loop through Involvements of previous version
    #         for invo in previous._involvements:
    #             oldinv_found = False
    #             for invn in self._involvements:
    #                 if (invo.get_guid() == invn.get_guid() and
    #                         invo.get_role() == invn.get_role()):
    #                     oldinv_found = True
    #                     break
    #             if oldinv_found is not True:
    #                 inv_old.append(invo.to_table(request))

    #         # Put it all together
    #         diff_object = {}
    #         if len(diff_new) > 0:
    #             diff_object['new_attr'] = diff_new
    #         if len(diff_old) > 0:
    #             diff_object['old_attr'] = diff_old
    #         if len(inv_old) > 0:
    #             diff_object['old_inv'] = inv_old
    #         if len(inv_new) > 0:
    #             diff_object['new_inv'] = inv_new

    #         # Only add diff object if not empty
    #         if diff_object != {}:
    #             self._diff_info['diff'] = diff_object

    # def get_order_value(self):
    #     return self._order_value

    # def get_previous_version(self):
    #     return self._previous_version


class ItemTaggroup(object):
    """
    TODO
    """

    def __init__(self, id, taggroup_id, main_tag_id):

        self._id = id
        self._taggroup_id = taggroup_id
        self._main_tag_id = main_tag_id

        self._tags = []

        self._main_tag = None

    @property
    def id(self):
        return self._id

    @property
    def taggroup_id(self):
        return self._taggroup_id

    @property
    def main_tag_id(self):
        return self._main_tag_id

    @property
    def tags(self):
        return self._tags

    @property
    def main_tag(self):
        return self._main_tag

    @main_tag.setter
    def main_tag(self, value):
        if isinstance(value, ItemTag):
            self._main_tag = value

    def add_tag(self, tag):
        """
        Add a new Tag to the internal Tag list. It is only added if it
        is a :class:`ItemTag` object.

        If the Tag has the same id as the Taggroup's MainTag, it is also
        set as the main_tag.

        Args:
            ``tag`` (:class:`ItemTag`): A :class:`ItemTag` object.
        """
        if isinstance(tag, ItemTag):
            self.tags.append(tag)
            if tag.id == self.main_tag_id:
                self.main_tag = tag

    def get_tag_by_id(self, id):
        """
        Return a tag based on its id.

        Args:
            ``id`` (int): The id of the Tag to be returned.

        Returns:
            :class:`ItemTag` or ``None``. The Tag or None if no Tag with
            the given id was found.
        """
        for t in self.tags:
            if t.id == id:
                return t
        return None

    # def __init__(self, id=None, tg_id=None, main_tag_id=None):
    #     """
    #     Create a new TagGroup object with id and the main_tag_id
    #     """

    #     # The TagGroup id
    #     self._id = id
    #     # The id of the main tag (not the tag itself!)
    #     self._main_tag_id = main_tag_id
    #     self._tg_id = tg_id
    #     # List to store the tags
    #     self._tags = []
    #     self._diffFlag = None
    #     # Geometry (only used for Activity TagGroups)
    #     self._geometry = None
    #     self._main_tag = None

    # def remove_tag(self, tag):
    #     if tag in self._tags:
    #         self._tags.remove(tag)

    # def get_id(self):
    #     return self._id

    # def get_tg_id(self):
    #     return self._tg_id

    # def get_maintag_id(self):
    #     return self._main_tag_id

    # def get_tag_by_key(self, key):
    #     """
    #     Returns a tag from this group if there is one with the requested key,
    #     else None is returned.
    #     """
    #     for t in self._tags:
    #         if t.get_key() == key:
    #             return t
    #     return None

    # def get_tags(self):
    #     return self._tags

    # def setDiffFlag(self, bool):
    #     self._diffFlag = bool

    # def getDiffFlag(self):
    #     return self._diffFlag

    # def set_geometry(self, geometry):
    #     self._geometry = geometry

    def to_json(self):
        """
        Return a JSON compatible representation of the Taggroup and its
        Tags.

        Returns:
            ``dict``. A dict containing the ids, MainTag and Tags of the
            Taggroup.
        """
        return {
            'id': self.id,
            'tg_id': self.taggroup_id,
            'main_tag': self.main_tag.to_json(),
            'tags': [t.to_json() for t in self.tags]
        }


class ItemTag(object):
    """
    TODO
    """

    def __init__(self, id, key, value):
        self._id = id
        self._key = key
        self._value = value

    @property
    def id(self):
        return self._id

    @property
    def key(self):
        return self._key

    @property
    def value(self):
        return self._value

    def to_json(self):
        """
        Return a JSON compatible representation of the Tag.

        Returns:
            ``dict``. A dict containing the id, key and value of the Tag.
        """
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value
        }
