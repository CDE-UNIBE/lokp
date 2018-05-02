/**
 * Creates a map, adds controlls to it and inserts it to a div with the same id as mapId
 */

// var editableLayers = new L.FeatureGroup();

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
        var geometry_type = options.geometry_type['geometry_type'];
        initDrawPolygonControl(map, geometry_type, mapId);


    }
    else {
        // Readonly! Add point and polygon areas to details page
        addDealLocationReadOnly(map, geometry); // geometry and dealAreas are defined in mapform.mak!!
        var coordinatesLatLong = geometry.coordinates;
        zoomToDealLocation(map, coordinatesLatLong);
        addDealAreasReadonly(map, dealAreas);
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
function addDealLocationReadOnly(map, geometry) {

    // get geometry field
    var $geometry = $(map.getContainer()).closest('div.taggroup').find('input[name = "geometry"]')

    if ($geometry !== null) {
        console.log('addDealLocationReadOnly');

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
function addDealAreasReadonly(map, dealAreas) {
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
    if (!jQuery.isEmptyObject(layerDictionary)) {  // only add layer control if layers aren't empty
        L.control.layers([], layerDictionary).addTo(map);
    }
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

/**
 * Parse coordinates entered in the textfield and writes it as input for the coordinates field
 */
function parseCoordinates(mapTitle) {
    if (mapTitle == 'map11') {


        var coordsField = $('#map-coords-field').val(); // read values from mak
        var coordsFormat = $('#map-coords-format').val();

        // Regex inspiration by: http://www.nearby.org.uk/tests/geotools2.js

        // It seems to be necessary to escape the values. Otherwise, the degree
        // symbol (°) is not recognized.
        var str = escape(coordsField);
        // However, we do need to replace the spaces again do prevent regex error.
        str = str.replace(/%20/g, ' ');

        var pattern, matches;
        var latsign, longsign, d1, m1, s1, d2, m2, s2;
        var latitude, longitude, latlong;

        if (coordsFormat == 1) {
            // 46° 57.1578 N 7° 26.1102 E
            pattern = /(\d+)[%B0\s]+(\d+\.\d+)\s*([NS])[%2C\s]+(\d+)[%B0\s]+(\d+\.\d+)\s*([WE])/i;
            matches = str.match(pattern);
            if (matches) {
                latsign = (matches[3] === 'S') ? -1 : 1;
                longsign = (matches[6] === 'W') ? -1 : 1;
                d1 = parseFloat(matches[1]);
                m1 = parseFloat(matches[2]);
                d2 = parseFloat(matches[4]);
                m2 = parseFloat(matches[5]);
                latitude = latsign * (d1 + (m1 / 60.0));
                longitude = longsign * (d2 + (m2 / 60.0));
                latlong = [latitude, longitude];
            }
        } else if (coordsFormat == 2) {
            // 46° 57' 9.468" N 7° 26' 6.612" E
            pattern = /(\d+)[%B0\s]+(\d+)[%27\s]+(\d+\.\d+)[%22\s]+([NS])[%2C\s]+(\d+)[%B0\s]+(\d+)[%27\s]+(\d+\.\d+)[%22\s]+([WE])/i;
            matches = str.match(pattern);
            if (matches) {
                latsign = (matches[4] === 'S') ? -1 : 1;
                longsign = (matches[8] === 'W') ? -1 : 1;
                d1 = parseFloat(matches[1]);
                m1 = parseFloat(matches[2]);
                s1 = parseFloat(matches[3]);
                d2 = parseFloat(matches[5]);
                m2 = parseFloat(matches[6]);
                s2 = parseFloat(matches[7]);
                latitude = latsign * (d1 + (m1 / 60.0) + (s1 / (60.0 * 60.0)));
                longitude = longsign * (d2 + (m2 / 60.0) + (s2 / (60.0 * 60.0)));
                latlong = [latitude, longitude];
            }
        } else if (coordsFormat == 3) {
            // N 46° 57.1578 E 7° 26.1102
            pattern = /([NS])\s*(\d+)[%B0\s]+(\d+\.\d+)[%2C\s]+([WE])\s*(\d+)[%B0\s]+(\d+\.\d+)/i;
            matches = str.match(pattern);
            if (matches) {
                latsign = (matches[1] === 'S') ? -1 : 1;
                longsign = (matches[4] === 'W') ? -1 : 1;
                d1 = parseFloat(matches[2]);
                m1 = parseFloat(matches[3]);
                d2 = parseFloat(matches[5]);
                m2 = parseFloat(matches[6]);
                latitude = latsign * (d1 + (m1 / 60.0));
                longitude = longsign * (d2 + (m2 / 60.0));
                latlong = [latitude, longitude];
            }
        } else if (coordsFormat == 4) {
            // N 46° 57' 9.468" E 7° 26' 6.612"
            pattern = /([NS])\s*(\d+)[%B0\s]+(\d+)[%27\s]+(\d+\.\d+)[%22%2C\s]+([WE])\s*(\d+)[%B0\s]+(\d+)[%27\s]+(\d+\.\d+)/i;
            matches = str.match(pattern);
            if (matches) {
                latsign = (matches[1] === 'S') ? -1 : 1;
                longsign = (matches[5] === 'W') ? -1 : 1;
                d1 = parseFloat(matches[2]);
                m1 = parseFloat(matches[3]);
                s1 = parseFloat(matches[4]);
                d2 = parseFloat(matches[6]);
                m2 = parseFloat(matches[7]);
                s2 = parseFloat(matches[8]);
                latitude = latsign * (d1 + (m1 / 60.0) + (s1 / (60.0 * 60.0)));
                longitude = longsign * (d2 + (m2 / 60.0) + (s2 / (60.0 * 60.0)));
                latlong = [latitude, longitude];
            }
        } else if (coordsFormat == 5) {
            // 46.95263, 7.43517
            pattern = /(\d+\.\d+)[%2C\s]+(\d+\.\d+)/i;
            matches = str.match(pattern);
            if (matches) {
                latlong = [matches[1], matches[2]];
            }
        }

        if (latlong != null) {
            // TODO use jquery instead?
            // Create the event. This way of event handling should be compatible with IE
            var event = new CustomEvent('sendCoordinates', {detail: latlong}); // create event and add coordinates

            // Define that the event name is 'build'.
            event.initEvent('sendCoordinates', true, true);


            // target can be any Element or other EventTarget.
            window.dispatchEvent(event);

        } else {
            showParseFeedback(tForInvalidFormat, 'error');
        }
    }
    return false;
}

/**
 * Function to show or hide the div to parse coordinates.
 */
function triggerCoordinatesDiv() {
    var coordinatesDiv = $('#coordinates-div');
    if (coordinatesDiv.is(':hidden')) {
        coordinatesDiv.show();
    } else {
        coordinatesDiv.hide();
    }
}

/**
 * Show a feedback after parsing the entered coordinates.
 * @param {String} msg
 * @param {String} textStyle
 */
function showParseFeedback(msg, textStyle) {
    var msgField = $('#map-coords-message');

    msgField.html([
        '<span class="text-',
        textStyle,
        '"></br>',
        msg,
        '</span>'
    ].join(''));
}

