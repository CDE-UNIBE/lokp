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
        <title>${_("Land Observatory")}</title>
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
        <script type="text/javascript" src="http://www.google.com/recaptcha/api/js/recaptcha_ajax.js"></script>
        <script type="text/javascript" src="${request.static_url('lmkp:static/lib/OpenLayers-2.11/OpenLayers.js')}"></script>
        <script type="text/javascript" src="http://maps.google.com/maps/api/js?v=3&amp;sensor=false"></script>
        <script type="text/javascript" src="${request.route_url('ui_translation')}"></script>
        <script type="text/javascript" src="${request.route_url('context_layers')}"></script>
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
        <script type="text/javascript" src="${request.static_url('lmkp:static/main-ext-all.js')}"></script>
        % endif
        <script type="text/javascript" src="${request.static_url('lmkp:static/app/main.js')}"></script>
    </head>
    <body>
        <div id="header-div">
            <div id="title-div">
                <h1>
                    ${_("Land Observatory")}
                </h1>
                <p>
                    ${_("The Land Observatory will make information on large-scale land acquisition transparent and accessible through an interactive, map-based platform. We are piloting the project in five countries, with partners and governments who will work to open government data, crowdsource and help customize local observatories. Updated information on land will benefit citizens, but also governments and companies interested in sustainability.")}
                </p>
                <p>
                    ${_("The pilot project is coordinated by the")}
                    <a href="http://www.landcoalition.org/">${_("International Land Coalition")}</a>
                    ${_("and the")}
                    <a href="http://www.cde.unibe.ch/">${_("Centre for Development and Environment")}</a>
                    ${_("at the University of Bern, Switzerland. It is funded by the")}
                    <a href="http://www.sdc.admin.ch/">${_("Swiss Agency for Development Cooperation")}</a>
                    ${_(", with co-funding from other ILC and CDE programs.")}
                </p>
            </div>
            <div id="logo-div">
                <a href="http://www.landportal.info/observatory">
                    <img src="${request.static_url('lmkp:static/img/lo-logo.png')}" height="100" width="100" alt="${_('Land Observatory')}"/>
                </a>
            </div>
        </div>
        <div id="loading-mask" style="width: 100%; height: 100%;">
            <div style="position: absolute; top: 50%; right: 50%">
                <img src="${request.static_url('lmkp:static/img/spinner.gif')}" alt="${_('loading')}"/>
            </div>
        </div>
        <div id="main-div"></div>
    </body>
</html>