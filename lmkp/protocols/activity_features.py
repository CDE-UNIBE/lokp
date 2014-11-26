import geojson
import json
from shapely import wkb
from shapely import geometry

from lmkp.models.database_objects import (
    Activity,
    Stakeholder,
)
from lmkp.views.form_config import getCategoryList
from lmkp.protocols.features import (
    ItemFeature,
    ItemTaggroup,
)
from lmkp.views.translation import get_translated_status
from lmkp.views.translation import statusMap


class ActivityFeature(ItemFeature):
    """
    TODO
    Extends the super class Feature and adds the geometry property
    """

    def __init__(self, identifier, order_value, version, status_id, geometry):

        ItemFeature.__init__(self, identifier, order_value, version, status_id)
        self._geometry = geometry

    @property
    def geometry(self):
        return self._geometry

    @geometry.setter
    def geometry(self, value):
        self._geometry = value

    # def getMappedClass(self):
    #     return Activity

    # def getOtherMappedClass(self):
    #     return Stakeholder

    # def to_tags(self, request):
    #     """
    #     Return a short representation in tag form (array of keys/values) of the
    #     most important attributes of the feature (as defined in the yaml as
    #     'involvementoverview')
    #     """

    #     categoryList = getCategoryList(request, 'activities')
    #     overviewkeys = categoryList.getInvolvementOverviewKeyNames()
    #     overviewtags = [{'key': k[0], 'value': []} for k in overviewkeys]

    #     for rettag in overviewtags:
    #         for tg in self._taggroups:
    #             for t in tg.get_tags():
    #                 if t.get_key() == rettag['key']:
    #                     rettag['value'].append(t.get_value())
    #         rettag['value'] = ', '.join(rettag['value'])

    #     return overviewtags

    # def get_geometry(self):
    #     geometry = None
    #     try:
    #         geom = wkb.loads(str(self._geometry.geom_wkb))
    #         geometry = json.loads(geojson.dumps(geom))
    #     except AttributeError:
    #         pass
    #     if isinstance(self._geometry, geojson.geometry.Point):
    #         geometry = json.loads(geojson.dumps(self._geometry))
    #     return geometry

    def to_json(self, request):
        """
        Return a JSON compatible representation of the :term:`Activity`.
        Builds on the ``ItemFeature.to_json`` function of the base class
        and adds the geometry of the :term:`Activity` to the dict.

        .. seealso::
           :class:`lmkp.protocols.features.ItemFeature.to_json`

        Args:
            ``request`` (pyramid.request): A :term:`Pyramid` Request
            object.

        Returns:
            ``dict``. A dict containing the id, Taggroups, status and
            version details, along with the geometry.
        """
        ret = super(ActivityFeature, self).to_json(request)
        if self.geometry is not None:
            try:
                geom = wkb.loads(str(self.geometry.geom_wkb))
                ret['geometry'] = geometry.mapping(geom)
            except:
                pass
        return ret

    # def to_table(self, request):
    #     """
    #     Returns a JSON compatible representation of this object
    #     """

    #     # Tag Groups
    #     tg = []
    #     for t in self._taggroups:
    #         tg.append(t.to_table())

    #     # Geometry
    #     geometry = None
    #     try:
    #         geom = wkb.loads(str(self._geometry.geom_wkb))
    #         geometry = json.loads(geojson.dumps(geom))
    #     except AttributeError:
    #         pass

    #     ret = {
    #         'id': self._guid,
    #         'taggroups': tg
    #     }

    #     if geometry is not None:
    #         ret['geometry'] = geometry
    #     if self._version is not None:
    #         ret['version'] = self._version
    #     if self._status is not None and self._status in statusMap:
    #         ret['status'] = get_translated_status(request, self._status)
    #     if self._status_id is not None:
    #         ret['status_id'] = self._status_id
    #     if self._timestamp is not None:
    #         ret['timestamp'] = str(self._timestamp)

    #     if self._previous_version is not None:
    #         ret['previous_version'] = self._previous_version

    #     institution = {}
    #     if self._institution_id is not None:
    #         institution['id'] = self._institution_id
    #     if self._institution_name is not None:
    #         institution['name'] = self._institution_name
    #     if self._institution_url is not None:
    #         institution['url'] = self._institution_url
    #     if self._institution_logo is not None:
    #         institution['logo'] = self._institution_logo
    #     if institution != {}:
    #         ret['institution'] = institution

    #     user = {}
    #     if self._user_id is not None:
    #         user['id'] = self._user_id
    #     if self._user_name is not None:
    #         user['username'] = self._user_name
    #     # User details based on privacy settings
    #     if self._user_privacy is not None and self._user_privacy > 0:
    #         if self._user_firstname is not None:
    #             user['firstname'] = self._user_firstname
    #         if self._user_lastname is not None:
    #             user['lastname'] = self._user_lastname
    #     if user != {}:
    #         ret['user'] = user

    #     # Involvements
    #     if len(self._involvements) != 0:
    #         sh = []
    #         for i in self._involvements:
    #             sh.append(i.to_table(request))
    #         ret['involvements'] = sh

    #     return ret


class ActivityTaggroup(ItemTaggroup):
    """
    TODO
    """

    def __init__(
            self, id=None, taggroup_id=None, main_tag_id=None, geometry=None):
        ItemTaggroup.__init__(self, id, taggroup_id, main_tag_id)
        self._geometry = geometry

    @property
    def geometry(self):
        return self._geometry

    @geometry.setter
    def geometry(self, value):
        self._geometry = value

    def to_json(self):
        """
        Return a JSON compatible representation of the :term:`Activity`
        Taggroup. Builds on the ``ItemTaggroup.to_json`` function of the
        base class and adds the Taggroup's geometry (if avilable) to the
        dict.

        .. seealso::
           :class:`lmkp.protocols.features.ItemTaggroup.to_json`

        Returns:
            ``dict``. A dict containing the id, key and value of the
            Taggroup, along with the geometry if available.
        """
        ret = super(ActivityTaggroup, self).to_json()
        if self.geometry is not None:
            try:
                geom = wkb.loads(str(self.geometry.geom_wkb))
                ret['geometry'] = geometry.mapping(geom)
            except:
                pass
        return ret
