<%inherit file="lmkp:templates/base.mak" />

<%def name="head_tags()">
<%

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
    ${_("Land Observatory")} - ${_("Moderation")}
    % if mode == 'demo':
        ${_("[Demo]")}
    % endif
</title>
<script type="text/javascript" src="${request.route_url('ui_translation')}"></script>
<script type="text/javascript" src="${request.route_url('edit_toolbar_config')}"></script>
% if use_js_builds:
<script type="text/javascript" src="${request.static_url('lmkp:static/moderation-ext-all.js')}"></script>
% endif
<script type="text/javascript" src="${request.static_url('lmkp:static/app/moderate.js')}"></script>

<script type="text/javascript">
    var openItem = "${openItem}";
    var type = "${type}";
    var identifier = "${identifier}";
</script>

<link rel="stylesheet" type="text/css" href="${request.static_url('lmkp:static/moderation.css')}"></link>
</%def>

<div id="loading-mask" style="width: 100%; height: 100%;">
    <div style="position: absolute; top: 50%; right: 50%">
        <img src="${request.static_url('lmkp:static/img/spinner.gif')}" alt="${_('gui_loading')}"/>
    </div>
</div>
<div id="main-div"></div>