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

%>
<title>${_("Land Observatory")} - ${_("Charts")}</title>
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
</%def>

<div id="loading-mask" style="width: 100%; height: 100%;">
    <div style="position: absolute; top: 50%; right: 50%">
        <img src="${request.static_url('lmkp:static/img/spinner.gif')}" alt="${_('Loading ...')} ..."/>
    </div>
</div>
<div id="heatmap-div">
    <h2>${_("Heat map for Cambodia and Laos")}</h2>
    <p>
        ${_("Distribution of land related deals in Cambodia and for Champasak and Attapeu province in Laos.")}<br/>
        ${_("Data for Cambodia are provided by the website")}
        <a href="http://www.opendevelopmentcambodia.net">www.opendevelopmentcambodia.net</a>.
        ${_("Data for Laos are based on the landconcessions database.")}
    </p>
    <p>
        <img src="${request.static_url('lmkp:static/img/activities_la_kh.png')}" alt="Distribution of activities in Cambodia and Laos (partly)"/>
    </p>
    <h2>${_("Distribution of activities worldwide")}</h2>
    <p>
        ${_("Worldwide distribution of land related deals based on the Landmatrix database available at")}
        <a href="http://www.landportal.info/landmatrix">
            www.landportal.info/landmatrix
        </a>
    </p>
    <p>
        <img src="${request.static_url('lmkp:static/img/worldwide_deals.png')}" alt="World-wide heatmap of activities"/>
    </p>
</div>
<div id="main-div"></div>