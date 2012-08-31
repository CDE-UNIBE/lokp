<?xml version="1.0" encoding="utf-8"?>
<%

import re
import geojson
import simplejson as json
from shapely import wkb
from shapely.geometry import asShape

%>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:georss="http://www.georss.org/georss"
      xmlns:gml="http://www.opengis.net/gml">
    <title>Activities</title>

    <subtitle>Activities on Observations on Land Acquisitions</subtitle>
    <link href="http://www.ola.org/"/>
    <updated>2005-12-13T18:30:02Z</updated>
    <author>
        <name>Centre for Development and Environment</name>
        <email>info@cde.unibe.ch</email>
    </author>
    <id>urn:uuid:60a76c80-d399-11d9-b93C-0003939e0af6</id>
    %for activity in data:
    <%

    geom = geojson.loads(json.dumps(activity['geometry']), object_hook=geojson.GeoJSON.to_instance)
    # The geometry
    shape = asShape(geom)

    coords = shape.representative_point()

    title = "%s: %s" % (activity['taggroups'][0]['main_tag']['key'],activity['taggroups'][0]['main_tag']['value'])

    taggroups = json.dumps(activity['taggroups'], indent=4)

    %>
    <entry>
        <title>${title}</title>
        <link href="http://localhost:6543/activities/${activity['id']}"/>
        <guid>urn:uuid:${activity['id']}</guid>
        <!--updated>2005-08-17T07:02:32Z</updated-->
        <summary>${taggroups}</summary>
        <georss:point>${coords.x} ${coords.y}</georss:point>
    </entry>
    %endfor
</feed>