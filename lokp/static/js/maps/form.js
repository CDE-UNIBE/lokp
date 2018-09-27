/**
 * Creates a map, adds controlls to it and inserts it to a div with the same id as mapId. This function can be used to
 * create a form map (used for geometry input) or for the map shown in the details page.
 *
 * mapId:   id of div container which should contain this map
 * options: dictionary containing the following options:
 *          pointsVisible: Boolean, points are displayed if true
 *           pointsCluster: Boolean, points are clustered if true
 *          geometry_type: Specifies whether this map allows drawing of 'point' or 'polygon'. Parameter required for form map.
 *
 *          ----Only for Details page (Readonly)----
 *          readonly: Specifies whether this map is added to readonly (=details) page or in the form
 *          dbLocationGeometry: point geometry with the location of this deal (from database).
 *          dbDealAreas: list of polygons for each intended area, contract area and current area.
 */
function createMap(mapId, options, geometry) {
    var baseLayers = getBaseLayers();
    var activeBaseLayer = Object.values(baseLayers)[0];
    var map = L.map(mapId, {
        layers: activeBaseLayer  // Initially only add first layer
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
    var mapOptions = {
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
    window.lokp_maps[mapId] = mapOptions;

    initBaseLayerControl();
    initMapContent(map);
    initPolygonLayers(mapId, window.mapVariables.polygon_keys);
    initContextLayerControl();
    initMapSearch(mapId);
    
    if (options.review === true) {
        var pointLatLngList = initComparisonPointMarkers(map, geometry);
        var areaLayerList = initComparisonPolygonLayers(map, geometry);
        zoomToFeatures(map, pointLatLngList, areaLayerList);
        return;
    }

    if (options.readonly !== true) {
        initDrawControl(mapOptions);
    }
    else {
        initDetailsMap(map, options);
    }
}


/*****************************************************
 * Helper Methods
 ****************************************************/


function zoomToFeatures(map, pointLatLngList, areaLayerList) {
    var bbox = L.latLngBounds();
    pointLatLngList.forEach(function(l) {
        bbox.extend(l);
    });
    areaLayerList.forEach(function(l) {
        bbox.extend(l.getBounds());
    });
    map.fitBounds(bbox);
    // If the map is zoomed in way too much (e.g. only 1 point on the map), the
    // map is not displayed correctly (no tiles). Set the zoom manually to
    // something more reasonable.
    if (map.getZoom() === map.getMaxZoom()) {
        map.setZoom(15);
    }
}


/**
 * Create a marker on the map and zoom to its location.
 * @param {L.map} map: The current map.
 * @param {array} geojsonCoords: Point coordinates in geojson format as array.
 */
function addPointMarker(map, geojsonCoords) {
    var latLng = L.GeoJSON.coordsToLatLng(geojsonCoords);
    L.marker(latLng).addTo(map);
    return latLng;
}

/**
 * For each polygon in dbDealAreas, a layer is added to the map in the details page. Also creates a layer control
 * (L.control) and adds the polygons to it, allowing the polygons to be toggled manually.
 *
 * @param map
 * @param dbDealAreas     Dictionary containing polygons for areas intended area, contract area current area
 */
function addDealAreasToLayerControl(map, dbDealAreas) {
    // iterate over dictionary
    var layerDictionary = [];
    var areaLayers = [];
    $.each(dbDealAreas, function (key, polygon) {  // method doku: http://api.jquery.com/jquery.each/
        var coords = polygon.coordinates;
        var coordsTransformed;
        if (polygon.type === 'Polygon') {
            coordsTransformed = coords.map(function(c) {
                return L.GeoJSON.coordsToLatLngs(c);
            });
        } else if (polygon.type === 'MultiPolygon') {
            coordsTransformed = coords.map(function(c2) {
                return c2.map(function(c1) {
                    return L.GeoJSON.coordsToLatLngs(c1);
                })
            });
        }
        var polygonL = L.polygon(
            coordsTransformed,
            {
                color: getPolygonColorByLabel(key)
            });
        areaLayers.push(polygonL);

        map.addLayer(polygonL); // polygons are initially added to the map
        layerDictionary[key] = polygonL;
    });

    // add Layers to layer control
    // try: https://gis.stackexchange.com/questions/178945/leaflet-customizing-the-layerswitcher
    // http://embed.plnkr.co/Je7c0m/
    if (!jQuery.isEmptyObject(layerDictionary)) {  // only add layer control if layers aren't empty
        L.control.layers([], layerDictionary).addTo(map);
    }
    return areaLayers;
}


function initDetailsMap(map, options) {
    var dbDealAreas = options.dbDealAreas;
    var pointLatLng = addPointMarker(map, options.dbLocationGeometry.coordinates);
    var areaLayerList = addDealAreasToLayerControl(map, dbDealAreas);
    zoomToFeatures(map, [pointLatLng], areaLayerList);
}

/**
 * Function is called when the 'parse' button is clicked. The entered coordinates are converted to a list of lat/long
 * coordinates. An event is dispatched containing the coordinates, which is then handled in drawPolygonFeature.js
 *
 * @param mapId: the id of the map container for which the function is called.
 */
function parseCoordinates(mapId) {
    var coordsField = $('#map-coords-field-' + mapId).val(); // read values from mak
    var coordsFormat = $('#map-coords-format-' + mapId).val();

    // Regex inspiration by: http://www.nearby.org.uk/tests/geotools2.js

    // It seems to be necessary to escape the values. Otherwise, the degree
    // symbol (°) is not recognized.
    var str = escape(coordsField);
    // However, we do need to replace the spaces again do prevent regex error.
    str = str.replace(/%20/g, ' ');

    var pattern, matches;
    var latsign, longsign, d1, m1, s1, d2, m2, s2;
    var latitude, longitude, latlong;

    if (coordsFormat === '1') {
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
    } else if (coordsFormat === '2') {
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
    } else if (coordsFormat === '3') {
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
    } else if (coordsFormat === '4') {
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
    } else if (coordsFormat === '5') {
        // 46.95263, 7.43517
        pattern = /(\d+\.\d+)[%2C\s]+(\d+\.\d+)/i;
        matches = str.match(pattern);
        if (matches) {
            latlong = [matches[1], matches[2]];
        }
    }

    if (latlong != null) {
        var mapOptions = getMapOptionsById(mapId);
        zoomAddSearchMarker(mapOptions, L.latLng(latlong), true);
        showParseFeedback(mapId, 'Coordinates successfully parsed.', 'success');
    } else {
        showParseFeedback(mapId, tForInvalidFormat, 'error');
    }
    return false;
}


/**
 * Show a feedback after parsing the entered coordinates.
 * @param {string} mapId
 * @param {String} msg
 * @param {String} textStyle
 */
function showParseFeedback(mapId, msg, textStyle) {
    var messageContainer = $('#map-actions-feedback-' + mapId);
    messageContainer.removeClass(function(index, className) {
        return (className.match (/(^|\s)alert-\S+/g) || []).join(' ');
    });
    messageContainer.addClass('alert-' + textStyle);
    messageContainer.find('.js-error-message').html(msg);
    messageContainer.show();
}

