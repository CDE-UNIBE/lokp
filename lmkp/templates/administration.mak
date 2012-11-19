<%inherit file="lmkp:templates/base.mak" />

<%def name="head_tags()">
<%

from pyramid.security import ACLAllowed
from pyramid.security import authenticated_userid
from pyramid.security import has_permission

if str(request.registry.settings['lmkp.use_js_builds']).lower() == "true":
    use_js_builds = True
else:
    use_js_builds = False

%>
<title>${_("Land Observatory")} - ${_("Administration")}</title>
## General Styles
<link rel="stylesheet" type="text/css" href="${request.static_url('lmkp:static/lib/extjs-4.1.1/resources/css/ext-all.css')}"></link>
<link rel="stylesheet" type="text/css" href="${request.static_url('lmkp:static/style.css')}"></link>
<script type="text/javascript" src="${request.static_url('lmkp:static/lib/extjs-4.1.1/ext.js')}"></script>
<script type="text/javascript">
    Ext.Loader.setConfig({
        enabled: true,
        paths: {
            'GeoExt': '/static/lib/geoext2/src/GeoExt',
            'Lmkp': '/static/app'
        }
    });
</script>
<script type="text/javascript" src="${request.route_url('ui_translation')}"></script>
<script type="text/javascript" src="${request.route_url('moderator_toolbar_config')}"></script>
<script type="text/javascript" src="${request.static_url('lmkp:static/app/admin.js')}"></script>
</%def>

<div id="loading-mask" style="width: 100%; height: 100%;">
    <div style="position: absolute; top: 50%; right: 50%">
        <img src="${request.static_url('lmkp:static/img/spinner.gif')}" alt="${_('gui_loading')}"/>
    </div>
</div>
<div id="main-div"></div>