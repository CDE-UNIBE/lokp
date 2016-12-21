<%inherit file="lmkp:templates/ext_base.mak" />

<%def name="head_tags()">
<%

from pyramid.security import ACLAllowed
from pyramid.security import authenticated_userid
from pyramid.security import has_permission

if str(request.registry.settings['lmkp.use_js_builds']).lower() == "true":
    use_js_builds = True
else:
    use_js_builds = False

mode = None
if 'lmkp.mode' in request.registry.settings:
    if str(request.registry.settings['lmkp.mode']).lower() == 'demo':
        mode = 'demo'
%>
<title>
    ${_("Myanmar land reporting")} - ${_("Administration")}
    % if mode == 'demo':
        ${_("[Demo]")}
    % endif
</title>
<script type="text/javascript" src="${request.route_url('ui_translation')}"></script>
% if use_js_builds:
<script type="text/javascript" src="${request.static_url('lmkp:static/administration-ext-all.js')}"></script>
% endif
<script type="text/javascript" src="${request.static_url('lmkp:static/app/admin.js')}"></script>
<link rel="stylesheet" type="text/css" href="${request.static_url('lmkp:static/administration.css')}"></link>
</%def>

<div id="loading-mask" style="width: 100%; height: 100%;">
    <div style="position: absolute; top: 50%; right: 50%">
        <img src="${request.static_url('lmkp:static/img/spinner.gif')}" alt="${_('Loading ...')}"/>
    </div>
</div>
<div id="main-div"></div>
