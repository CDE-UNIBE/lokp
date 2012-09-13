<%

from pyramid.security import ACLAllowed
from pyramid.security import authenticated_userid
from pyramid.security import has_permission

if str(request.registry.settings['lmkp.use_js_builds']).lower() == "true":
    use_js_builds = True
else:
    use_js_builds = False

%>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <title>Land Observatory</title>
        <link rel="stylesheet" type="text/css" href="${request.static_url('lmkp:static/lib/extjs-4.1.1/resources/css/ext-all.css')}"></link>
        <link rel="stylesheet" type="text/css" href="${request.static_url('lmkp:static/style.css')}"></link>
        <script type="text/javascript" src="${request.static_url('lmkp:static/lib/extjs-4.1.1/ext.js')}"></script>
        <script type="text/javascript">
            Ext.Loader.setConfig({
                % if use_js_builds:
                enabled: false
                % else:
                enabled: true,
                paths: {
                    'GeoExt': '/static/lib/geoext2/src/GeoExt',
                    'Lmkp': '/static/app'
                }
                % endif
            });
        </script>
        <script type="text/javascript" src="/lang"></script>
        % if isinstance(has_permission('administer', request.context, request), ACLAllowed):
        <script type="text/javascript" src="/app/view/EditToolbar.js"></script>
        % elif isinstance(has_permission('moderate', request.context, request), ACLAllowed):
        <script type="text/javascript" src="/app/view/EditToolbar.js"></script>
        % elif isinstance(has_permission('edit', request.context, request), ACLAllowed):
        <script type="text/javascript" src="/app/view/EditToolbar.js"></script>
        % else:
        <script type="text/javascript" src="/app/view/ViewToolbar.js"></script>
        % endif
        % if use_js_builds:
        <script type="text/javascript" src="${request.static_url('lmkp:static/charts-ext-all.js')}"></script>
        % endif
        <script type="text/javascript" src="${request.static_url('lmkp:static/app/charts.js')}"></script>
    </head>
    <body>
        <div id="header-div">
            <h1>Land Observatory</h1>
            <p>Some introductory text about the project etc.</p>
            <p>Maybe also a nice logo?</p>
        </div>
        <div id="loading-mask" style="width: 100%; height: 100%;">
            <div style="position: absolute; top: 50%; right: 50%">
                <img src="/static/img/spinner.gif"/>
            </div>
        </div>
        <div id="heatmap-div">
            <h2>Heat map for Cambodia and Laos</h2>
            <p>
                Distribution of land related deals in Cambodia and for
                Champasak and Attapeu province in Laos.<br/>
                Data for Cambodia are provided by the website
                <a href="http://www.opendevelopmentcambodia.net">www.opendevelopmentcambodia.net</a>.
                Data for Laos are based on the landconcessions database.
            </p>
            <p>
                <img src="${request.static_url('lmkp:static/img/activities_la_kh.png')}" alt="Distribution of activities in Cambodia and Laos (partly)"/>
            </p>
            <h2>Distribution of activities worldwide</h2>
            <p>
                Worldwide distribution of land related deals based on the
                Landmatrix database available at <a href="http://www.landportal.info/landmatrix">
                    www.landportal.info/landmatrix
                </a>
            </p>
            <p>
                <img src="${request.static_url('lmkp:static/img/worldwide_deals.png')}" alt="World-wide heatmap of activities"/>
            </p>
        </div>
        <div id="main-div"></div>
    </body>
</html>