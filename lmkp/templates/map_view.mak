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
        margin-bottom: 15px;
        cursor: pointer;
    }
    .map-legend-content {
        display: none;
        margin-bottom: 15px;
    }
    .map-menu b.caret {
        margin: 8px 5px 0 0;
    }
</style>
<script type="text/javascript">
<%

from lmkp.views.profile import _getCurrentProfileExtent
import json

extent = json.dumps(_getCurrentProfileExtent(request))

%>
        var profilePolygon = ${extent | n};
    
</script>
</%def>

## Start of content

<!-- Filter-area  -->
<form class="form-horizontal filter_area">
    <div class="container">
        <div class="control-group">
            <label class="control-label">Active filters</label>
            <div class="controls">
                <input type="text" id="filter1" class="filter-variable1" placeholder="A sample variable > 23" />
                <span class="icon-remove1">
                    <i class="icon-remove pointer"></i>
                </span>
            </div>
        </div>
        <div class="control-group">
            <div class="controls">
                <input type="text" id="filter2" class="filter-variable2" placeholder="Another sample variable = Cambodia" />
                <span class="icon-remove2">
                    <i class="icon-remove pointer"></i>
                </span>
            </div>
        </div>
        <div class="control-group new-filter new-filter">
            <label class="control-label">New Filter</label>
            <div class="controls">
                <div class="btn-group">
                    <button class="btn select_btn_filter">Taggroup</button>
                    <button class="btn select_btn_filter_right dropdown-toggle" data-toggle="dropdown">
                        <span class="caret"></span>
                    </button>
                    <ul class="dropdown-menu">
                        <li><a href="#">1</a></li>
                        <li><a href="#">2</a></li>
                        <li><a href="#">3</a></li>
                        <li><a href="#">4</a></li>
                        <li><a href="#">5</a></li>
                    </ul>
                </div>

                <div class="btn-group">
                    <button class="btn select_btn_operator">&#8804;</button>
                    <button class="btn select_btn_operator_right dropdown-toggle" data-toggle="dropdown">
                        <span class="caret"></span>
                    </button>
                    <ul class="dropdown-menu">
                        <li><a href="#">&#8805;</a></li>
                        <li><a href="#">=</a></li>
                        <li><a href="#">!=</a></li>
                    </ul>
                </div>
                <input type="text" class="filter-value" id="filter2" placeholder="Value" />
                <span class="icon-add">
                    <i class="icon-plus pointer"></i>
                </span>
            </div>
        </div>
        <div class="favorite">
            <div class="btn-group favorite">
                <button class="btn btn_favorite">Favorite</button>
                <button class="btn btn_favorite_right dropdown-toggle" data-toggle="dropdown">
                    <span class="caret"></span>
                </button>
                <ul class="dropdown-menu">
                    <li><a href="#">1</a></li>
                    <li><a href="#">2</a></li>
                    <li><a href="#">3</a></li>
                    <li><a href="#">4</a></li>
                    <li><a href="#">5</a></li>
                </ul>
            </div>
        </div>
    </div>
</form>

<div class="filter_area_openclose">
    <i class="icon-double-angle-down pointer"></i>
    <span class="pointer">Click here to add or edit a filter</span>
    <i class="icon-double-angle-down pointer"></i>
</div>

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
        <!--input type="submit" value="Search" id="search-submit" /-->
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

<%def name="bottom_tags()">
<script type="text/javascript" src="http://maps.google.com/maps/api/js?v=3&amp;sensor=false"></script>
<script src="${request.static_url('lmkp:static/lib/OpenLayers-2.12/OpenLayers.js')}" type="text/javascript"></script>
<script type="text/javascript" src="${request.route_url('context_layers2')}"></script>
<script src="${request.static_url('lmkp:static/v2/map.js')}" type="text/javascript"></script>
<script src="${request.static_url('lmkp:static/v2/filters.js')}" type="text/javascript"></script>
<script src="${request.static_url('lmkp:static/v2/jquery.cookie.js')}" type="text/javascript"></script>
</%def>