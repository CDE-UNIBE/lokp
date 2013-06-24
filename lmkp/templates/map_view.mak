<%inherit file="lmkp:templates/htmlbase.mak" />

<%def name="title()">Map View</%def>

<%def name="head_tags()">
<link rel="stylesheet" href="${request.static_url('lmkp:static/lib/OpenLayers-2.12/theme/default/style.css')}" type="text/css">
<style type="text/css" >
    .olTileImage {
        max-width: none !important;
    }
    .olControlAttribution {
        bottom: 0px;
        left: 3px;
    }
    .legendEntry {
        font-size: 0.8em;
        margin-bottom: 2px;
        margin-top: 2px;
    }
    .vectorLegendSymbol {
        float: left;
        height: 20px;
        margin-right: 5px;
        width: 20px;
    }
</style>
<script src="${request.static_url('lmkp:static/lib/OpenLayers-2.12/OpenLayers.js')}" type="text/javascript"></script>
<script type="text/javascript" src="http://maps.google.com/maps/api/js?v=3&amp;sensor=false"></script>
<script type="text/javascript" src="${request.route_url('context_layers2')}"></script>
</%def>

## Start of content

<!-- Filter-area  -->
<form class="form-horizontal filter_area">
    <div class="container">
        <div class="control-group">
            <label class="control-label">Active filters</label>
            <div class="controls">
                <input type="text" id="filter1" class="filter-variable1" placeholder="A sample variable > 23">
                <span class="icon-remove1">
                    <i class="icon-remove pointer"></i>
                </span>
            </div>
        </div>
        <div class="control-group">
            <div class="controls">
                <input type="text" id="filter2" class="filter-variable2" placeholder="Another sample variable = Cambodia">
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
                <input type="text" class="filter-value" id="filter2" placeholder="Value">
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
    <i class="icon-double-angle-up pointer"></i>
</div>

<!-- content -->
<div class="no-border">
    <div class="map-whole-page shadow-inside">
        <div id="map-div" style="width: 100%; height: 100%;"></div>
    </div>
    <div class="shadow-inside"></div>
</div>

<div class="basic-data" style="z-index: 1100;">
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
<div class="map-menu" style="z-index: 1100;">
    <form class="navbar-search" action="">
        <input name="q" id="search" class="search-query" placeholder="search location">
        <input type="submit" value="Search" id="search-submit">
    </form><br>
    <!-- Base layers -->
    <div class="map-menu-base-layers">
        <h6>Base layers</h6>
        <ul>
            <li>
                <label class="radio inline">
                    <input type="radio" class="baseMapOptions" name="baseMapOptions" id="streetMapOption" value="streetMap" checked>Street Map</label>
            </li>
            <li>
                <label class="radio inline">
                    <input type="radio" class="baseMapOptions" name="baseMapOptions" id="satelliteMapOption" value="satelliteMap">Satellite Imagery</label>
            </li>
            <li>
                <label class="radio inline">
                    <input type="radio" class="baseMapOptions" name="baseMapOptions" id="terrainMapOption" value="terrainMap">Terrain Map</label>
            </li>
        </ul>
    </div>

    <hr class="lightgray">

    <!-- Context layers -->
    <div class="map-menu-context-layers">
        <h6>Context layers</h6>
        <ul id="context-layers-list">
            <!--
            <li>
                <div class="checkbox-modified-small">
                    <input class="input-top" type="checkbox" value="Accessibility" id="checkboxAccessibility">
                    <label for="checkboxAccessibility"></label>
                </div>
                <p class="context-layers-description">
                    Accessibility&nbsp;
                    <i class="icon-exclamation-sign pointer"></i>
                </p>
            </li>
            <li>
                <div class="checkbox-modified-small">
                    <input class="input-top" type="checkbox" value="PopulationDensity2008" id="checkboxPopulationDensity2008">
                    <label for="checkboxPopulationDensity2008"></label>
                </div>
                <p class="context-layers-description">
                    Population Density 2008&nbsp;
                    <i class="icon-exclamation-sign pointer"></i>
                </p>
            </li>
            <li>
                <div class="checkbox-modified-small">
                    <input class="input-top" type="checkbox" value="GlobalLandCover2009" id="checkboxGlobalLandCover2009">
                    <label for="checkboxGlobalLandCover2009"></label>
                </div>
                <p class="context-layers-description">
                    Global LandCover 2009&nbsp;
                    <i class="icon-exclamation-sign pointer"></i>
                </p>
            </li>
            <li>
                <div class="checkbox-modified-small">
                    <input class="input-top" type="checkbox" value="GlobalCropland" id="checkboxGlobalCropland">
                    <label for="checkboxGlobalCropland"></label>
                </div>
                <p class="context-layers-description">
                    Global Cropland&nbsp;
                    <i class="icon-exclamation-sign pointer"></i>
                </p>
            </li>
            <li>
                <div class="checkbox-modified-small">
                    <input class="input-top" type="checkbox" value="GlobalPastureLand" id="checkboxGlobalPastureLand">
                    <label for="checkboxGlobalPastureLand"></label>
                </div>
                <p class="context-layers-description">
                    Global Pasture Land&nbsp;
                    <i class="icon-exclamation-sign pointer"></i>
                </p>
            </li>-->
        </ul>
    </div>
</div>

<!-- legend menu -->
<div class="legend-menu" style="z-index: 1100;">
    <h6>Map Legend</h6>
    <ul id="map-legend-list">
        <!--  Placeholder for map legend entries -->
    </ul>
</div>

## End of content

<%def name="bottom_tags()">
<script src="${request.static_url('lmkp:static/v2/map.js')}" type="text/javascript"></script>
<script src="${request.static_url('lmkp:static/v2/filters.js')}" type="text/javascript"></script>
<script src="${request.static_url('lmkp:static/v2/jquery.cookie.js')}" type="text/javascript"></script>
</%def>