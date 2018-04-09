/**
 * For Map Content (Activities)
 * mapValues
 * mapCriteria
 * aKeys
 * shKeys
 *
 * tForChangesInThisSection
 *
 */
function createReviewMap(mapId, geometry) {

    console.log('geometryCompare', geometry)
    var baseLayers = getBaseLayers();
    var activeBaseLayer = Object.values(baseLayers)[0];
    var map = L.map(mapId, {
        layers: activeBaseLayer,  // Initially only add first layer
        //drawControl: true           // enables display of draw toolbar
    });


    // get geometries
    var pointRefDeal = geometry.ref.geometry;
    var pointNewDeal = geometry.new.geometry;

    // add deal locations to map
    addDealLocation(map, pointRefDeal);
    addDealLocation(map, pointNewDeal);

    // zoom to new deal location
    var coordNewDeal = pointNewDeal.coordinates;
    zoomToDealLocation(map, coordNewDeal);

    var dealAreasRef = JSON.parse(geometry.ref.dealAreas);
    var dealAreasNew = JSON.parse(geometry.new.dealAreas);

    addDealAreaLayers(dealAreasNew, dealAreasRef, map);

    // addDealAreaLayers(dealAreasRef, map);


    // Object.keys(dealAreasNew);
    // TODO list of dictionaries


    // JSON.parse(geometry.new.dealAreas)[key]

    // TODO: add both geometries to the map


//     map.on('moveend', function (e) {
//         $.cookie('_LOCATION_', map.getBounds().toBBoxString(), {expires: 7});
//     });
//
//     // Initial map extent
//     var initialExtent = L.geoJSON(window.mapVariables.profile_polygon).getBounds();
//     var locationCookie = $.cookie('_LOCATION_');
//     if (locationCookie) {
//         // If a valid cookie is set, use this as extent
//         var parts = locationCookie.split(',');
//         if (parts.length === 4) {
//             initialExtent = L.latLngBounds(
//                 L.latLng(parts[1], parts[0]),
//                 L.latLng(parts[3], parts[2]));
//         }
//     }
//     map.fitBounds(initialExtent);
//
//     // Disable dragging of the map for the floating buttons
//     var ctrl = L.DomUtil.get('map-floating-buttons-' + mapId);
//     if (ctrl) {
//         ctrl.addEventListener('mouseover', function () {
//             map.dragging.disable();
//         });
//         ctrl.addEventListener('mouseout', function () {
//             map.dragging.enable();
//         });
//     }
//
//     // Hide loading overlay
//     $('.map-loader[data-map-id="' + mapId + '"]').hide();
//
//     if (typeof window.lokp_maps === 'undefined') {
//         window.lokp_maps = {};
//     }
//     window.lokp_maps[mapId] = {
//         map: map,
//         baseLayers: baseLayers,
//         contextLayers: getContextLayers(mapId, window.mapVariables.context_layers),
//         polygonLayers: {},
//         // Keep track of the currently active base layer so it can be changed
//         // programmatically
//         activeBaseLayer: activeBaseLayer,
//         activeMapMarker: null,
//         // Initial map variables
//         mapVariables: window.mapVariables,
//         options: options
//     };
//
    initBaseLayerControl();
    // initMapContent(map);
    initPolygonLayers(mapId, window.mapVariables.polygon_keys);
    initContextLayerControl();
    initMapSearch(mapId);

    // if (options.readonly !== true) {
    //     var geometry_type = options.geometry_type['geometry_type']
    //     initDrawPolygonControl(map, geometry_type);
    //
    //     // TODO: make this work for edit as well (geometries are not passed to edit mode)
    // }
    // else {
    //     // Readonly! Add point and polygon areas to details page
    //     addDealLocation(map, geometry); // geometry and dealAreas are defined in mapform.mak!!
    //     zoomToDealLocation(map, geometry);
    //     addDealAreas(map, dealAreas);
    // }
}


/*****************************************************
 * Helper Methods
 ****************************************************/

/**
 * @param map           Map created by createMapForm
 * @param geometry      Point which is added to map
 */
function addDealLocation(map, geometry) {
    if (geometry !== null) {
        // change coordinates to lat/long
        var coordLatLong = geometry.coordinates.reverse();
        L.marker(coordLatLong).addTo(map); // custom item can be set here
    }
}


// TODO: move this to base.js
function zoomToDealLocation(map, coordLatLong) {
    var lat = coordLatLong[0];
    var long = coordLatLong[1];
    map.setView([lat, long], 8);
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
        console.log(key + ": " + polygon)
        // convert to leaflet polygon
        var polyCoords = polygon.coordinates;
        polyCoords = polyCoords[0]; // remove unnecessary array depth

        // change each long lat coordinate within polyCoords to lat long
        polyCoordsLatLon = changeToLatLon(polyCoords);

        var polygonL = L.polygon(polyCoordsLatLon, {color: 'blue'});
        layerDictionary[key] = polygonL;

        // TODO: add checkbox (html code can be passed with key) http://leafletjs.com/reference-1.3.0.html#control-layers
    });

    // add Layers to layer control
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

// see form.js
/**
 * @param dealAreasNew      JSON containing the name (Intended area (ha) etc.) and the coordinates of each dealArea of the new data
 * @param dealAreasRef      JSON containing the name and the coordinates of each dealArea of the reference data
 * @param map               The Id to which the deal areas are added.
 */
function addDealAreaLayers(dealAreasNew, dealAreasRef, map) {

    // get deal areas as dictionaries (key: Intended Area etc., value a polygonlayer))
    var layerDictionaryNew = getDictWithGeometries(dealAreasNew, map, false);
    var layerDictionaryRef = getDictWithGeometries(dealAreasRef, map, true);

    // combine dictionaries
    var dictLayers = Object.assign({}, layerDictionaryNew, layerDictionaryRef);

    // add to layer control
    L.control.layers([], dictLayers).addTo(map);
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

/**
 * Returns dictionary containing all deal areas. Adds each deal area to the map.
 * @param dealAreas             Deal areas as JSON object
 * @param map                   The map to add layers to
 * @param isReferenceData       Boolean. If true, layerLabel is changed to avoid duplicates
 */
function getDictWithGeometries(dealAreas, map, isReferenceData) {
    // iterate over each
    var keys = Object.keys(dealAreas); // keys are Intended Area, Current area in operation
    var layerDictionary = {};
    for (var i = 0; i < keys.length; i++) {
        var coordinates = dealAreas[keys[i]].geometry.coordinates;
        coordinates = coordinates[0]; // flatten list
        var coordinatesLatLong = changeToLatLon(coordinates);

        var layerLabel = keys[i];
        var layerColor = getLayerColor(layerLabel);

        // create layer and set it's color depending on the deal area's name
        var layer = L.polygon(coordinatesLatLong, {color: layerColor});

        // cut last 5 characters and add new suffix to label
        layerLabel = layerLabel.slice(0, -5);
        layerLabel = isReferenceData ? layerLabel + "_Ref" : layerLabel + "_New";


        map.addLayer(layer); // makes polygons appear when map is first loaded
        layerDictionary[layerLabel] = layer;
    }
    return layerDictionary;
}

/**
 * returns a string containing the layer's color
 * @param layerLabel
 */
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

// TODO: move this to base.js
function zoomToDealLocation(map, coordLatLong) {
    var lat = coordLatLong[0];
    var long = coordLatLong[1];
    map.setView([lat, long], 7);
}