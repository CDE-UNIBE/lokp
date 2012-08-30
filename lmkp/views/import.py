import uuid

from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession as Session
import psycopg2
from pyramid.view import view_config
from shapely.geometry import asShape
from sqlalchemy import distinct
from sqlalchemy import func
from sqlalchemy.sql.expression import cast
from sqlalchemy.types import Float

@view_config(route_name='lao_import', renderer='json')
def lao_import(request):

    connection = psycopg2.connect("dbname=landconcessions user=stefan password=stefan host=localhost")

    cursor = connection.cursor()

    # Execute a command: this creates a new table

    sql = "SELECT * FROM (SELECT ST_AsGeoJSON(ST_Union(ST_Transform(the_geom, 4326))) AS json_geometry, "
    sql = sql + "project_code FROM data.geo_point WHERE data.geo_point.project_code "
    sql = sql + "ILIKE \'05%\' GROUP BY project_code) AS p "
    sql = sql + "JOIN data.project ON data.project.project_code=p.project_code;"

    print sql

    cursor.execute(sql)

    result = []
    for a_record in cursor:

        sh_cursor = connection.cursor()

        #**********************************************************************#
        # Handle first the stakeholder
        #**********************************************************************#
        # Get the stakeholder id
        sh_id = a_record[7]

        # Get the full stakeholder info from the db:
        sh_query = "SELECT data.lut_company.id, data.lut_company.name_eng, data.lut_country.name_eng "
        sh_query = sh_query + "FROM data.lut_company LEFT JOIN data.lut_country "
        sh_query = sh_query + "ON data.lut_company.id_country = data.lut_country.id WHERE data.lut_company.id = "
        sh_query = sh_query + str(sh_id) + ";"

        sh_cursor.execute(sh_query)

        existing_sh = None
       
        for sh_record in sh_cursor:
            print "***********************************************"
            print existing_sh
            #result.append({'origin_db_id': sh_record[0], 'Name': sh_record[1], 'Country': sh_record[2]})
            
            # Check first if stakeholder already exists
            existing_sh = Session.query(Stakeholder).filter(SH_Key.key == 'origin_db_id').filter(SH_Value.value == str(sh_record[0])).first()

            # Create the stakeholder if it does not exist
            if existing_sh is None:

                new_stakeholder = Stakeholder(uuid.uuid4(), 1)
                new_stakeholder.fk_status = 1

                # Create a tag group
                sh_taggroup = SH_Tag_Group()
                new_stakeholder.tag_groups.append(sh_taggroup)
                # Create a Name tag
                if sh_record[0] is not None:
                    sh_taggroup.tags.append(create_tag(request, 'origin_db_id', sh_record[0]))
                if sh_record[1] is not None:
                    sh_taggroup.tags.append(create_tag(request, 'Name', sh_record[1]))
                if sh_record[2] is not None:
                    sh_taggroup.tags.append(create_tag(request, 'Country', sh_record[2]))

                Session.add(new_stakeholder)

                # The stakeholder that is connected to the activity through an involvement
                existing_sh = new_stakeholder

                print "***********************************************"
                print existing_sh

        #**********************************************************************#
        # Handle the activity
        #**********************************************************************#
        geojson_obj = geojson.loads(a_record[0], object_hook=geojson.GeoJSON.to_instance)
        geojson_shape = asShape(geojson_obj)

        value = a_record[4]

        taggroup = A_Tag_Group()

        k = Session.query(A_Key).filter(A_Key.key == 'Name').first()
        # If the value is not yet in the database, create a new value
        v = Session.query(A_Value).filter(A_Value.value == unicode(value)).first()
        if v is None:
            v = A_Value(value=value)
            v.fk_language = 1

        # Create a new tag with key and value and append it to the parent tag group
        a_tag = A_Tag()
        taggroup.tags.append(a_tag)
        a_tag.key = k
        a_tag.value = v

        activity_identifier = uuid.uuid4()
        new_activity = Activity(activity_identifier, 1, geojson_shape.representative_point().wkt)
        new_activity.fk_status = 1
        new_activity.tag_groups.append(taggroup)

        Session.add(new_activity)

        #**********************************************************************#
        # The involvement
        #**********************************************************************#
        new_involvement = Involvement()
        new_involvement.fk_activity = Session.query(Activity.id).filter(Activity.activity_identifier == activity_identifier).first()[0]
        new_involvement.fk_stakeholder = existing_sh.id
        new_involvement.fk_stakeholder_role = 6
        Session.add(new_involvement)

        result.append({"a": new_activity, "sh": existing_sh, "i": new_involvement})

    return result


def create_tag(request, key, value):
    """
    Create a new tag
    """
    tag = SH_Tag()
    k = Session.query(SH_Key).filter(SH_Key.key == key).first()
    # If the value is not yet in the database, create a new value
    v = Session.query(SH_Value).filter(SH_Value.value == unicode(value)).first()
    if v is None:
        v = SH_Value(value=value)
        v.fk_language = 1
    tag.key = k
    tag.value = v

    return tag