import json
import logging
from geoalchemy.postgis import (
    functions,
    pg_functions,
)
from pyramid.i18n import TranslationStringFactory
from pyramid.view import view_config
from sqlalchemy import (
    func,
    or_,
)
from sqlalchemy.sql.expression import literal_column

from lmkp.models.database_objects import Geonames
from lmkp.models.meta import DBSession as Session
from lmkp.views.views import BaseView

_ = TranslationStringFactory('lmkp')
log = logging.getLogger(__name__)


class LocationSearchView(BaseView):

    @view_config(route_name='location_search', renderer="json")
    def search(self):

        if "q" not in self.request.params:
            return {"success": False, "msg": "Parameter 'q' is missing."}

        q = self.request.params["q"]

        if "epsg" in self.request.params:
            epsg = int(self.request.params["epsg"])
            geometry = functions.transform(Geonames.wkb_geometry, epsg)
        else:
            geometry = Geonames.wkb_geometry

        filters = [
            func.lower(Geonames.name).like(func.lower(q + "%")),
            func.lower(Geonames.asciiname).like(func.lower(q + "%")),
            func.lower(Geonames.alternatenames).like(func.lower(q + "%"))]

        rows = []

        for geojson, name, fcode, country in Session.query(
            pg_functions.geojson(geometry), Geonames.name, Geonames.fcode,
            Geonames.country).\
            filter(or_(*filters)).order_by(
                literal_column('bit_length("name")').label("word_length")).\
                all():
            rows.append({
                "name": "%s, %s, %s" % (name, fcode, country),
                "geometry": json.loads(geojson)})

        return {"success": True, "data": rows}
