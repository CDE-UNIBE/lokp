<%inherit file="lmkp:templates/htmlbase.mak" />

<%def name="title()">Map View</%def>

<%def name="head_tags()">
<link rel="stylesheet" href="${request.static_url('lmkp:static/lib/OpenLayers-2.12/theme/default/style.css')}" type="text/css" />
<style type="text/css" >
    .olTileImage {
        max-width: none !important;
    }
    .olControlAttribution {
        bottom: 0px;
        left: 10px;
    }
    .legendEntry {
        font-size: 0.8em;
        margin-bottom: 2px !important;
        margin-top: 2px;
    }
    .vectorLegendSymbol {
        float: left;
        height: 20px;
        margin-right: 5px;
        width: 20px;
    }
    .context-layers {
        margin-bottom: 0;
    }
    .base-layers-content {
        margin-bottom: 15px;
    }
    .map-legend {
        margin-bottom: 5px;
        cursor: pointer;
    }
    .map-legend-content {
        margin-bottom: 15px;
    }
    .map-menu b.caret {
        margin: 8px 5px 0 0;
    }
    #deal-shortid-span a {
        color: inherit;
        font-weight: normal;
    }
    #mapModal h3 {
        padding-top: 0;
    }
</style>
<script type="text/javascript">
<%

from lmkp.views.profile import _getCurrentProfileExtent
from lmkp.views.views import getOverviewKeys
import json

aKeys, shKeys = getOverviewKeys(request)
extent = json.dumps(_getCurrentProfileExtent(request))

%>
    var profilePolygon = ${extent | n};
    var aKeys = ${json.dumps(aKeys) | n};
    var shKeys = ${json.dumps(shKeys) | n};
    
</script>
</%def>

## Start of content

## Filter
<%include file="lmkp:templates/parts/filter.mak" />

<!-- content -->
<div id="googleMapFull">
    <!--  Placeholder for the map -->
</div>

<div class="basic-data">
    <h6 class="deal-headline">Deal
        <span id="deal-shortid-span" class="underline">#</span>
    </h6>
    <ul id="taggroups-ul">
        <li>
            <p>No deal selected.</p>
        </li>
    </ul>
</div>

<!-- map menu -->
<div class="map-menu">
    <form class="navbar-search" action="">
        <input name="q" id="search" class="search-query" placeholder="search location" />
        <input value="Search" id="search-submit" />
    </form><br/>

    <!-- Base layers -->
    <div class="map-menu-base-layers">
        <h6 class="base-layers"><b class="caret"></b>Base layers</h6>
        <div class="base-layers-content">
            <ul>
                <li>
                    <label class="radio inline"><input type="radio" class="baseMapOptions" name="baseMapOptions" id="streetMapOption" value="streetMap" checked />Street Map</label>
                </li>
                <li>
                    <label class="radio inline"><input type="radio" class="baseMapOptions" name="baseMapOptions" id="satelliteMapOption" value="satelliteMap" />Satellite Imagery</label>
                </li>
                <li>
                    <label class="radio inline"><input type="radio" class="baseMapOptions" name="baseMapOptions" id="terrainMapOption" value="terrainMap" />Terrain Map</label>
                </li>
            </ul>
        </div>
    </div>

    <!-- Context layers -->
    <div class="map-menu-context-layers">
        <h6 class="context-layers"><b class="caret"></b>Context layers</h6>
        <div class="context-layers-content">
            <ul id="context-layers-list">
                <!--  Placeholder for context layers entries -->
            </ul>
        </div>
    </div>

    <!-- Map legend -->
    <div class="map-menu-legend">
        <h6 class="map-legend"><b class="caret"></b>Map Legend</h6>
        <div class="map-legend-content">
            <ul id="map-legend-list">
                <!--  Placeholder for map legend entries -->
            </ul>
        </div>
    </div>
</div>

## End of content

<div id="mapModal" class="modal fade hide">
    <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
        <h3 id="mapModalHeader"><!-- Placeholder --></h3>
    </div>
    <div id="mapModalBody" class="modal-body">
        <!-- Placeholder -->
    </div>
    <div class="modal-footer">
        <button id="mapModalClose" class="btn" data-dismiss="modal" aria-hidden="true">Close</button>
    </div>
</div>

<%def name="bottom_tags()">
<script type="text/javascript" src="http://maps.google.com/maps/api/js?v=3&amp;sensor=false"></script>
<script src="${request.static_url('lmkp:static/lib/OpenLayers-2.12/OpenLayers.js')}" type="text/javascript"></script>
<script type="text/javascript" src="${request.route_url('context_layers2')}"></script>
<script src="${request.static_url('lmkp:static/v2/map.js')}" type="text/javascript"></script>
<script src="${request.static_url('lmkp:static/v2/filters.js')}" type="text/javascript"></script>
<script src="${request.static_url('lmkp:static/v2/jquery.cookie.js')}" type="text/javascript"></script>
</%def>