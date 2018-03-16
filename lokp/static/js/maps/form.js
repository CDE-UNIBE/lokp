/**
 * Creates a map, adds controlls to it and inserts it to a div with the same id as mapId
 */
function createFormMap(mapId, options) {
    console.log('call createFormMap function ' + mapId);
    var baseLayers = getBaseLayers();
    var activeBaseLayer = Object.values(baseLayers)[0];
    var map = L.map(mapId, {
        layers: activeBaseLayer,  // Initially only add first layer
        drawControl: true           // enables display of draw toolbar
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
        initDrawPolygonControl(map);


        // TODO: make this work for edit as well (geometries are not passed to edit mode)
    }
    else {
        // adds the location point of the deal shown in details page to the detail's page map
        addDealLocation(map, geometry); // geometry and dealAreas are defined in mapform.mak!!
        zoomToDealLocation(map, geometry);
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

function zoomToDealLocation(map, geometry) {
    var coordLatLong = geometry.coordinates.reverse();
    //L.panTo(coordLatLong);
    //L.setZoom(5);
}

/**
 * @param map
 * @param dealAreas     Dictionary containing polygons for areas intended area, contract area current area
 // TODO: DICTIONARY INSTEAD OF LIST?
 // draw polygon when reloading page
 */
function addDealAreas(map, dealAreas) {

    dealAreas.forEach(function (polygon) {
        // convert to leaflet polygon
        var polyCoords = polygon.coordinates;
        polyCoords = polyCoords[0]; // remove unnecessary array depth

        // change each long lat coordinate within polyCoords to lat long
        polyCoordsLatLon = changeToLatLon(polyCoords);

        console.log('polyCoordsLatLon', polyCoordsLatLon);
        console.log('polyCoords', polyCoords);
        var polygonL = L.polygon(polyCoordsLatLon, {color: 'red'}).addTo(map);
    });
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
