from lmkp.models.database_objects import *
from lmkp.models.meta import DBSession as Session
from pyramid.view import view_config
from sqlalchemy import func

@view_config(route_name='sitemap', renderer='lmkp:templates/sitemap.mak')
def sitemap_xml(request):

    request.response.content_type = "text/xml"

    host = request.environ['HTTP_HOST']
    scheme = request.environ['wsgi.url_scheme']

    urls = []
    for activity, lastmod in Session.query(Activity, func.to_char(Activity.timestamp_entry,'YYYY-MM-DD')).\
        join(Status).filter(Status.name == "active").limit(25000).all():
        loc = request.route_url("activities_read_one", output="html", uid=activity.activity_identifier)
        urls.append({"loc": loc, "lastmod": lastmod})

    for stakeholder, lastmod in Session.query(Stakeholder, func.to_char(Stakeholder.timestamp_entry,'YYYY-MM-DD')).\
        join(Status).filter(Status.name == "active").limit(25000).all():
        loc = request.route_url("stakeholders_read_one", output="html", uid=stakeholder.stakeholder_identifier)
        urls.append({"loc": loc, "lastmod": lastmod})
    

    return {"urls": urls}

    