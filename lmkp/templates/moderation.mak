<%inherit file="lmkp:templates/base.mak" />

<%def name="head_tags()">

<title>${_("Land Observatory")} - ${_("Moderation")}</title>
<script type="text/javascript" src="${request.route_url('ui_translation')}"></script>
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