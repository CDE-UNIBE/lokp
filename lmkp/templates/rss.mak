<?xml version="1.0" encoding="utf-8"?>
<%

import re
from shapely import wkb

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
        attributes = ['id', 'timestamp', 'version', 'geometry']

        entry = {}
        for a in attributes:
            entry[a] = activity.__dict__[a]

        d = re.search("[0-9]{4}-[0-9]{2}-[0-9]{2}", str(entry['timestamp'])).group(0)
        t = re.search("[0-9]{2}:[0-9]{2}:[0-9]{2}", str(entry['timestamp'])).group(0)
        entry['timestamp'] = '{day}T{time}Z'.format(day=d, time=t)

        if activity.__dict__['Name'] is not None:
            entry['name'] = activity.__dict__['Name']
        else:
            entry['name'] = "Activity id %s" % entry['id']

        coords = wkb.loads(str(entry['geometry'].geom_wkb))
    %>
    <entry>
        <title>${entry['name']}</title>
        <link href="http://localhost:6543/activities/${entry['id']}"/>
        <guid>urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a</guid>
        <!--updated>2005-08-17T07:02:32Z</updated-->
        <updated>${entry['timestamp']}</updated>
        <summary>${entry['name']}</summary>
        <georss:point>${coords.x} ${coords.y}</georss:point>
    </entry>
    %endfor
</feed>