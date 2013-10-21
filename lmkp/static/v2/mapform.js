/**
 * Necessary variables with translated text for this file (must be defined and
 * translated in template):
 * tForSuccess
 * tForInvalidFormat
 */

var geographicProjection = new OpenLayers.Projection("EPSG:4326");
var sphericalMercatorProjection = new OpenLayers.Projection("EPSG:900913");
var map;
var geojsonFormat = new OpenLayers.Format.GeoJSON({
    'internalProjection': sphericalMercatorProjection,
    'externalProjection': geographicProjection
});

$(document).ready(function() {
    var layers = getBaseLayers();
    var geometryLayer = new OpenLayers.Layer.Vector('Geometry', {
        styleMap: new OpenLayers.StyleMap({
            'default': OpenLayers.Util.applyDefaults({
                externalGraphic: '/static/img/pin_darkred.png',
                graphicHeight: 25,
                graphicOpacity: 0.8,
                graphicYOffset: -25
            }, OpenLayers.Feature.Vector.style["default"])
        }),
        eventListeners: {
            'featureadded': updateFormCoordinates
        }
    });
    layers.push(geometryLayer);

    map = new OpenLayers.Map('googleMapNotFull', {
        displayProjection: geographicProjection,
        projection: sphericalMercatorProjection,
        controls: [
            new OpenLayers.Control.Attribution(),
            new OpenLayers.Control.Navigation({
                dragPanOptions: {
                    enableKinetic: true
                }
            }),
            new OpenLayers.Control.PanZoom()
        ],
        layers: layers
    });

    if (coordsSet === true) {
        geometryLayer.addFeatures(geojsonFormat.read(geometry));
        // Zoom to the feature
        map.zoomToExtent(geometryLayer.getDataExtent());
        // Adjust zoom level
        map.zoomTo(Math.min(zoomlevel, map.getZoom()-1));
    } else {
        if (bbox) {
            map.zoomToExtent(bbox, true);
        } else {
            map.zoomToMaxExtent();
        }
    }

    if (!readonly) {
        $('#googleMapNotFull').css('cursor', "crosshair");

        map.events.register('click', map, function(e) {
            var position = map.getLonLatFromPixel(e.xy);
            addToMap(position);
        });

        // Listen to 'paste' events on the coordinate field
        $('#map-coords-field').on('paste', function() {
            setTimeout(function() {
                parseCoordinates();
            }, 50);
        });
    }
});

/**
 * Set a marker on the map at the given position and store the coordinates in
 * the hidden field.
 */
function addToMap(lonlat) {
    if (lonlat.CLASS_NAME != 'OpenLayers.LonLat') return;
    var layers = map.getLayersByName('Geometry');
    if (layers.length == 0) return;
    var geometryLayer = layers[0];
    var p = new OpenLayers.Geometry.Point(lonlat.lon, lonlat.lat);
    var f = new OpenLayers.Feature.Vector(p);
    if (editmode === 'singlepoint') {
        geometryLayer.destroyFeatures();
        geometryLayer.addFeatures([f]);
    }
}

/**
 * Update the form field containing the coordinates based on the feature in the
 * geometry layer.
 */
function updateFormCoordinates(event) {
    var feature;
    if (event && event.feature && event.feature.geometry) {
        feature = event.feature;
    } else {
        var layers = map.getLayersByName('Geometry');
        if (layers.length == 0) return;
        var geometryLayer = layers[0];
        if (!geometryLayer.features || geometryLayer.features.length != 1
            || !geometryLayer.features[0].geometry) return;
        feature = geometryLayer.features[0];
    }
    var field = $('input[name=geometry]');
    if (field.length != 1) return;
    $(field[0]).val(geojsonFormat.write(feature.geometry));
}

/**
 * Return the base layers of the map.
 */
function getBaseLayers(){

    var layers = [];

    // Try to get the Google Satellite layer
    try {
        layers.push(new OpenLayers.Layer.Google("satelliteMap", {
            type: google.maps.MapTypeId.HYBRID,
            numZoomLevels: 22
        }));

        layers.push(new OpenLayers.Layer.Google("terrainMap", {
            type: google.maps.MapTypeId.TERRAIN
        }));
    // else get backup layers that don't block the application in case there
    // is no internet connection.
    } catch(error) {
        layers.push(new OpenLayers.Layer.OSM("satelliteMap", [
            "http://oatile1.mqcdn.com/tiles/1.0.0/sat/${z}/${x}/${y}.jpg",
            "http://oatile2.mqcdn.com/tiles/1.0.0/sat/${z}/${x}/${y}.jpg",
            "http://oatile3.mqcdn.com/tiles/1.0.0/sat/${z}/${x}/${y}.jpg",
            "http://oatile4.mqcdn.com/tiles/1.0.0/sat/${z}/${x}/${y}.jpg"
            ],{
                attribution: "<p>Tiles Courtesy of <a href=\"http://www.mapquest.com/\" target=\"_blank\">MapQuest</a> <img src=\"http://developer.mapquest.com/content/osm/mq_logo.png\"></p>",
                isBaseLayer: true,
                sphericalMercator: true,
                projection: new OpenLayers.Projection("EPSG:900913")
            }));
    }

    layers.push(new OpenLayers.Layer.OSM("streetMap", [
        "http://otile1.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg",
        "http://otile2.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg",
        "http://otile3.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg",
        "http://otile4.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg"
        ],{
            attribution: "<p>Tiles Courtesy of <a href=\"http://www.mapquest.com/\" target=\"_blank\">MapQuest</a> <img src=\"http://developer.mapquest.com/content/osm/mq_logo.png\"></p>",
            isBaseLayer: true,
            sphericalMercator: true,
            projection: sphericalMercatorProjection,
            transitionEffect: "resize"
        }));

    return layers;
}

/**
 * Parse coordinates entered in the textfield.
 * Coordinates are assumed to always be in WGS84.
 */
function parseCoordinates() {

    var coordsField = $('#map-coords-field').val();
    var coordsFormat = $('#map-coords-format').val();

    // Regex inspiration by: http://www.nearby.org.uk/tests/geotools2.js

    // It seems to be necessary to escape the values. Otherwise, the degree
    // symbol (°) is not recognized.
    var str = escape(coordsField);
    // However, we do need to replace the spaces again do prevent regex error.
    str = str.replace(/%20/g, ' ');

    var pattern, matches;
    var latsign, longsign, d1, m1, s1, d2, m2, s2;
    var latitude, longitude, lonlat;

    if (coordsFormat == 1) {
        // 46° 57.1578 N 7° 26.1102 E
        pattern = /(\d+)[%B0\s]+(\d+\.\d+)\s*([NS])[%2C\s]+(\d+)[%B0\s]+(\d+\.\d+)\s*([WE])/i;
        matches = str.match(pattern);
        if (matches) {
            latsign = (matches[3]=='S') ? -1 : 1;
            longsign = (matches[6]=='W') ? -1 : 1;
            d1 = parseFloat(matches[1]);
            m1 = parseFloat(matches[2]);
            d2 = parseFloat(matches[4]);
            m2 = parseFloat(matches[5]);
            latitude = latsign * (d1 + (m1/60.0));
            longitude = longsign * (d2 + (m2/60.0));
            lonlat = new OpenLayers.LonLat(longitude, latitude);
        }
    } else if (coordsFormat == 2) {
        // 46° 57' 9.468" N 7° 26' 6.612" E
        pattern = /(\d+)[%B0\s]+(\d+)[%27\s]+(\d+\.\d+)[%22\s]+([NS])[%2C\s]+(\d+)[%B0\s]+(\d+)[%27\s]+(\d+\.\d+)[%22\s]+([WE])/i;
        matches = str.match(pattern);
        if (matches) {
            latsign = (matches[4]=='S') ? -1 : 1;
            longsign = (matches[8]=='W') ? -1 : 1;
            d1 = parseFloat(matches[1]);
            m1 = parseFloat(matches[2]);
            s1 = parseFloat(matches[3]);
            d2 = parseFloat(matches[5]);
            m2 = parseFloat(matches[6]);
            s2 = parseFloat(matches[7]);
            latitude = latsign * (d1 + (m1/60.0) + (s1/(60.0*60.0)));
            longitude = longsign * (d2 + (m2/60.0) + (s2/(60.0*60.0)));
            lonlat = new OpenLayers.LonLat(longitude, latitude);
        }
    } else if (coordsFormat == 3) {
        // N 46° 57.1578 E 7° 26.1102
        pattern = /([NS])\s*(\d+)[%B0\s]+(\d+\.\d+)[%2C\s]+([WE])\s*(\d+)[%B0\s]+(\d+\.\d+)/i;
        matches = str.match(pattern);
        if (matches) {
            latsign = (matches[1]=='S') ? -1 : 1;
            longsign = (matches[4]=='W') ? -1 : 1;
            d1 = parseFloat(matches[2]);
            m1 = parseFloat(matches[3]);
            d2 = parseFloat(matches[5]);
            m2 = parseFloat(matches[6]);
            latitude = latsign * (d1 + (m1/60.0));
            longitude = longsign * (d2 + (m2/60.0));
            lonlat = new OpenLayers.LonLat(longitude, latitude);
        }
    } else if (coordsFormat == 4) {
        // N 46° 57' 9.468" E 7° 26' 6.612"
        pattern = /([NS])\s*(\d+)[%B0\s]+(\d+)[%27\s]+(\d+\.\d+)[%22%2C\s]+([WE])\s*(\d+)[%B0\s]+(\d+)[%27\s]+(\d+\.\d+)/i;
        matches = str.match(pattern);
        if (matches) {
            latsign = (matches[1]=='S') ? -1 : 1;
            longsign = (matches[5]=='W') ? -1 : 1;
            d1 = parseFloat(matches[2]);
            m1 = parseFloat(matches[3]);
            s1 = parseFloat(matches[4]);
            d2 = parseFloat(matches[6]);
            m2 = parseFloat(matches[7]);
            s2 = parseFloat(matches[8]);
            latitude = latsign * (d1 + (m1/60.0) + (s1/(60.0*60.0)));
            longitude = longsign * (d2 + (m2/60.0) + (s2/(60.0*60.0)));
            lonlat = new OpenLayers.LonLat(longitude, latitude);
        }
    } else if (coordsFormat == 5) {
        // 46.95263, 7.43517
        pattern = /(\d+\.\d+)[%2C\s]+(\d+\.\d+)/i;
        matches = str.match(pattern);
        if (matches) {
            lonlat = new OpenLayers.LonLat(matches[2], matches[1]);
        }
    }

    if (lonlat != null) {
        // Transform the coordinates.
        var lonlatTransformed = lonlat.transform(
            new OpenLayers.Projection("EPSG:4326"),
            map.getProjectionObject()
        );

        // Set the marker and zoom to it.
        addToMap(lonlatTransformed);
        map.setCenter(lonlatTransformed);

        showParseFeedback(tForSuccess, 'success');
    } else {
        showParseFeedback(tForInvalidFormat, 'error');
    }
    return false;
}

/**
 * Function to show or hide the div to parse coordinates.
 */
function triggerCoordinatesDiv() {
    var coordinatesDiv = $('#coordinates-div');
    if (coordinatesDiv.is(':visible')) {
        coordinatesDiv.hide();
    } else {
        coordinatesDiv.show();
    }
}

/**
 * Show a feedback after parsing the entered coordinates.
 */
function showParseFeedback(msg, textStyle) {
    var msgField = $('#map-coords-message');
    msgField.html([
        '<span class="text-',
        textStyle,
        '">',
        msg,
        '</span>'
    ].join(''));
}