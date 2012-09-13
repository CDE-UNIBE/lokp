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
        ## General Styles
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
        <script type="text/javascript" src="${request.route_url('ui_translation')}"></script>
        % if isinstance(has_permission('administer', request.context, request), ACLAllowed):
        <script type="text/javascript" src="${request.route_url('moderator_toolbar_config')}"></script>
        % elif isinstance(has_permission('moderate', request.context, request), ACLAllowed):
        <script type="text/javascript" src="${request.route_url('moderator_toolbar_config')}"></script>
        % elif isinstance(has_permission('edit', request.context, request), ACLAllowed):
        <script type="text/javascript" src="${request.route_url('edit_toolbar_config')}"></script>
        % else:
        <script type="text/javascript" src="${request.route_url('view_toolbar_config')}"></script>
        % endif
        % if use_js_builds:
        <script type="text/javascript" src="${request.static_url('lmkp:static/charts-ext-all.js')}"></script>
        % endif
        <script type="text/javascript" src="${request.static_url('lmkp:static/app/charts.js')}"></script>
    </head>
    <body>
        <div id="header-div">
            <div id="title-div">
                <h1>Land Observatory</h1>
                <p>
                    The Land Observatory will make information on large-scale land acquisition
                    transparent and accessible through an interactive, map-based platform.
                    We are piloting the project in five countries, with partners and governments
                    who will work to open government data, crowdsource and help customize local observatories.
                    Updated information on land will benefit citizens, but also governments
                    and companies interested in sustainability.
                </p>
                <p>
                    The pilot project is coordinated by the
                    <a href="http://www.landcoalition.org/">International Land Coalition</a>
                    and the
                    <a href="http://www.cde.unibe.ch/">Centre for Development and Environment</a> at the University of Bern, Switzerland.
                    It is funded by the <a href="http://www.sdc.admin.ch/">Swiss Agency for Development Cooperation</a>,
                    with co-funding from other ILC and CDE programs.​
                </p>
            </div>
            <div id="logo-div">
                <img src="${request.static_url('lmkp:static/img/lo-logo.png')}" height="100" width="100" alt="Land Observatory"/>
            </div>
        </div>
        <div id="loading-mask" style="width: 100%; height: 100%;">
            <div style="position: absolute; top: 50%; right: 50%">
                <img src="${request.static_url('lmkp:static/img/spinner.gif')}" alt="loading ..."/>
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