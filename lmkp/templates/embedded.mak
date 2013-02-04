<%inherit file="lmkp:templates/base.mak" />

<%def name="head_tags()">
<%

from pyramid.security import effective_principals
principals = effective_principals(request)

%>
<title>${_("Land Observatory")}</title>
<script type="text/javascript" src="http://www.google.com/recaptcha/api/js/recaptcha_ajax.js"></script>
<script type="text/javascript" src="${request.static_url('lmkp:static/lib/OpenLayers-2.11/OpenLayers.js')}"></script>
<script type="text/javascript" src="http://maps.google.com/maps/api/js?v=3&amp;sensor=false"></script>
<script type="text/javascript" src="${request.route_url('ui_translation')}"></script>
<script type="text/javascript" src="${request.route_url('context_layers')}"></script>
% if 'group:moderators' in principals:
<script type="text/javascript" src="${request.route_url('moderator_toolbar_config')}"></script>
% elif 'group:editors' in principals:
<script type="text/javascript" src="${request.route_url('edit_toolbar_config')}"></script>
% else:
<script type="text/javascript" src="${request.route_url('view_toolbar_config')}"></script>
% endif
% if use_js_builds:
<script type="text/javascript" src="${request.static_url('lmkp:static/main-ext-all.js')}"></script>
% endif
<script type="text/javascript" src="${request.static_url('lmkp:static/app/main.js')}"></script>
<script type="text/javascript">
    Ext.ns('Lmkp');
    Lmkp.is_embedded = true;
</script>
</%def>

<div id="loading-mask" style="width: 100%; height: 100%;">
    <div style="position: absolute; top: 50%; right: 50%">
        <img src="${request.static_url('lmkp:static/img/spinner.gif')}" alt="${_('gui_loading')}"/>
    </div>
</div>
<div id="main-div"></div>