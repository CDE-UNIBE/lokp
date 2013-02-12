<%inherit file="lmkp:templates/base.mak" />

<%def name="head_tags()">
<%

from pyramid.security import ACLAllowed
from pyramid.security import authenticated_userid
from pyramid.security import has_permission

mode = None
if 'lmkp.mode' in request.registry.settings:
    if str(request.registry.settings['lmkp.mode']).lower() == 'demo':
        mode = 'demo'
%>
<title>
    % if mode == 'demo':
        [Demo]
    % endif
    ${_("Land Observatory")} - ${_("Administration")}
</title>
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