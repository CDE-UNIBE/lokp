/**
 * Creates a map, adds controlls to it and inserts it to a div with the same id as mapId
 */
function createFormMap(mapId, options) {


    console.log('call createFormMap function ' + mapId);
    var baseLayers = getBaseLayers();
    var activeBaseLayer = Object.values(baseLayers)[0];
    var map = L.map(mapId, {
        layers: activeBaseLayer,  // Initially only add first layer
        //drawControl: true           // enables display of draw toolbar
    });
    map.on('moveend', function (e) {
        $.cookie('_LOCATION_', map.getBounds().toBBoxString(), {expires: 7});
    });

    // Initial map extent
    var initialExtent = L.geoJSON(window.mapVariables.profile_polygon).getBounds();
    var locationCookie = $.cookie('_LOCATION_');
    if (locationCookie) {
        // If a valid cookie is set, use this as extent
        var parts = locationCookie.split(',');
        if (parts.length === 4) {
            initialExtent = L.latLngBounds(
                L.latLng(parts[1], parts[0]),
                L.latLng(parts[3], parts[2]));
        }
    }
    map.fitBounds(initialExtent);

    // Disable dragging of the map for the floating buttons
    var ctrl = L.DomUtil.get('map-floating-buttons-' + mapId);
    if (ctrl) {
        ctrl.addEventListener('mouseover', function () {
            map.dragging.disable();
        });
        ctrl.addEventListener('mouseout', function () {
            map.dragging.enable();
        });
    }

    // Hide loading overlay
    $('.map-loader[data-map-id="' + mapId + '"]').hide();

    if (typeof window.lokp_maps === 'undefined') {
        window.lokp_maps = {};
    }
    window.lokp_maps[mapId] = {
        map: map,
        baseLayers: baseLayers,
        contextLayers: getContextLayers(mapId, window.mapVariables.context_layers),
        polygonLayers: {},
        // Keep track of the currently active base layer so it can be changed
        // programmatically
        activeBaseLayer: activeBaseLayer,
        activeMapMarker: null,
        // Initial map variables
        mapVariables: window.mapVariables,
        options: options
    };

    initBaseLayerControl();
    initMapContent(map);
    initPolygonLayers(mapId, window.mapVariables.polygon_keys);
    initContextLayerControl();
    initMapSearch(mapId);

    if (options.readonly !== true) {
        var geometry_type = options.geometry_type['geometry_type']
        initDrawPolygonControl(map, geometry_type);


        // TODO: make this work for edit as well (geometries are not passed to edit mode)
    }
    else {
        // Readonly! Add point and polygon areas to details page
        addDealLocation(map, geometry); // geometry and dealAreas are defined in mapform.mak!!
        var coordinatesLatLong = geometry.coordinates;
        zoomToDealLocation(map, coordinatesLatLong);
        addDealAreas(map, dealAreas);
    }
}


/*****************************************************
 * Helper Methods
 ****************************************************/

/**
 *
 * @param map           Map created by createMapForm
 * @param geometry      Polygon or Point which is added to map
 */
function addDealLocation(map, geometry) {

    // get geometry field
    var $geometry = $(map.getContainer()).closest('div.taggroup').find('input[name = "geometry"]')

    if ($geometry !== null) {
        console.log('addDealLocation');

        // change coordinates to lat/long
        var coordLatLong = geometry.coordinates.reverse();

        L.marker(coordLatLong).addTo(map); // custom item can be set here
    }
}


/**
 * @param map
 * @param dealAreas     Dictionary containing polygons for areas intended area, contract area current area

 // draw polygon when reloading page
 */
function addDealAreas(map, dealAreas) {
    // iterate over dictionary

    var layerDictionary = [];
    $.each(dealAreas, function (key, polygon) {  // method doku: http://api.jquery.com/jquery.each/
        // convert to leaflet polygon
        var polyCoords = polygon.coordinates;
        polyCoords = polyCoords[0]; // remove unnecessary array depth

        // change each long lat coordinate within polyCoords to lat long
        var polyCoordsLatLon = changeToLatLon(polyCoords);

        var layerColor = getLayerColor(key);

        var polygonL = L.polygon(polyCoordsLatLon, {color: layerColor});
        map.addLayer(polygonL); // polygons are initially added to the map
        layerDictionary[key] = polygonL;

        // TODO: add checkbox (html code can be passed with key) http://leafletjs.com/reference-1.3.0.html#control-layers
    });

    // add Layers to layer control
    // try: https://gis.stackexchange.com/questions/178945/leaflet-customizing-the-layerswitcher
    // http://embed.plnkr.co/Je7c0m/
    L.control.layers([], layerDictionary).addTo(map);

}

/**
 *
 * @param polyCoords An array containing arrays with a long/lat coordinate pair (for each vertex of the polygon)
 * @returns {Array} An array containing arrays with a lat/long coordinate pair
 */
function changeToLatLon(polyCoords) {
    var polyCoordsLatLon = [];
    for (var i = 0; i < polyCoords.length; i++) {
        var coordLongLat = polyCoords[i];
        var coordLatLong = coordLongLat.reverse();
        polyCoordsLatLon.push(coordLatLong);
    }
    return polyCoordsLatLon;
}

function zoomToDealLocation(map, coordLatLong) {
    var lat = coordLatLong[0];
    var long = coordLatLong[1];
    map.setView([lat, long], 8);
}

// TODO: move to base
function getLayerColor(layerLabel) {
    var layerColor;
    if (layerLabel == 'Intended area (ha)') {  // TODO: get string config
        layerColor = 'lightgreen';
    }
    if (layerLabel == 'Contract area (ha)') {
        layerColor = 'green';
    }
    if (layerLabel == 'Current area in operation (ha)') {
        layerColor = 'blue';
    }
    return layerColor
}