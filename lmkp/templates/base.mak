<%

import json
from lmkp.views.translation import language_store
from lmkp.views.profile import profile_store

available_languages = json.dumps(language_store(request), ensure_ascii=True)
available_profiles = json.dumps(profile_store(request), ensure_ascii=True)

if str(request.registry.settings['lmkp.use_js_builds']).lower() == "true":
    use_js_builds = True
else:
    use_js_builds = False

comments_url = request.registry.settings['lmkp.comments_url']

%>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <link rel="stylesheet" type="text/css" href="${request.static_url('lmkp:static/lib/extjs-4.1.1/resources/css/ext-all.css')}"></link>
        <link rel="stylesheet" type="text/css" href="${request.static_url('lmkp:static/style.css')}"></link>
        <script type="text/javascript" src="${request.static_url('lmkp:static/lib/extjs-4.1.1/ext.js')}"></script>
        <script type="text/javascript" src="${request.static_url('lmkp:static/lib/extjs-4.1.1/ext.js')}"></script>
        <!-- Make sure Ext.util.Cookies is available -->
        <script type="text/javascript" src="${request.static_url('lmkp:static/lib/extjs-4.1.1/src/util/Cookies.js')}"></script>
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
            Ext.ns('Lmkp');
            Lmkp.available_languages = ${available_languages | n};
            Lmkp.available_profiles = ${available_profiles | n};
            Lmkp.comments_url = "${comments_url}";
        </script>
        ${self.head_tags()}
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
        ${self.body()}
    </body>
</html>