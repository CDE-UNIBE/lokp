/**
 * Necessary variables with translated text for this file (must be defined and
 * translated in template):
 * tForSuccess
 * tForInvalidFormat
 *
 *
 * For Map Content (Activities)
 * mapValues
 * mapCriteria
 * aKeys
 * shKeys
 * areaNames
 * readonly
 */

var geographicProjection = new OpenLayers.Projection("EPSG:4326");
var sphericalMercatorProjection = new OpenLayers.Projection("EPSG:900913");
var geojsonFormat = new OpenLayers.Format.GeoJSON({
    'internalProjection': sphericalMercatorProjection,
    'externalProjection': geographicProjection
});
var selectCtrl,
    geometryLayer,
    removeLayer;

$(document).ready(function() {

    /** Settings **/
    pointsCluster = false;
    pointsVisible = false;
    mapInteractive = false;
    contextLegendInformation = false;
    polygonLoadOnStart = false;

    /**
     * Map and layers
     */
    var layers = getBaseLayers();
    var markerStyle = new OpenLayers.StyleMap({
        'default': OpenLayers.Util.applyDefaults({
            externalGraphic: '/static/img/pin_darkred.png',
            graphicHeight: 25,
            graphicOpacity: 0.8,
            graphicYOffset: -25
        }, OpenLayers.Feature.Vector.style["default"])
    });
    removeLayer = new OpenLayers.Layer.Vector('RemovePoints', {
        styleMap: markerStyle,
        eventListeners: {
            'featureselected': removeFeature
        }
    });
    layers.push(removeLayer);
    geometryLayer = new OpenLayers.Layer.Vector('Geometry', {
        styleMap: markerStyle,
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
            new OpenLayers.Control.Zoom({
                zoomInId: 'btn-zoom-in',
                zoomOutId: 'btn-zoom-out'
            })
        ],
        layers: layers
    });
    setBaseLayerByName(map, 'satelliteMap');
    initializeThisPolygonContent();
    initializeMapContent();
    initializeContextLayers();
    initializePolygonLayers();

    /**
     * Map Events
     */
     initializeBaseLayerControl();
     initializeContextLayerControl();
     initializePolygonLayerControl();
     initializeMapSearch();

    $('.form-map-menu-toggle').click(function() {
        $('#form-map-menu-content').toggle();
        var m = $('.form-map-menu');
        m.toggleClass('active');
        if (m.hasClass('active')) {
            $(this).button('close');
        } else {
            $(this).button('reset');
        }
        return false;
    });

    if (coordsSet === true) {
        geometryLayer.addFeatures(geojsonFormat.read(geometry));
        // Map is zoomed only after adding any polygon layers to prevent it from
        // zooming twice.
    } else {
        if (bbox) {
            map.zoomToExtent(bbox, true);
        } else {
            map.zoomToMaxExtent();
        }
    }

    if (!readonly) {

        selectCtrl = new OpenLayers.Control.SelectFeature(removeLayer);
        map.addControl(selectCtrl);

        toggleMode('add');

        map.events.register('click', map, function(e) {
            if (geometryLayer.getVisibility()) {
                var position = map.getLonLatFromPixel(e.xy);
                addToMap(position);
            }
        });

        // Listen to 'paste' events on the coordinate field
        $('#map-coords-field').on('paste', function() {
            setTimeout(function() {
                parseCoordinates();
            }, 50);
        });

        $('#btn-add-point').click(function() {
            toggleMode('add');
        });
        $('#btn-remove-point').click(function() {
            toggleMode('remove');
        });
    }

    $('.collapse').on('show', function() {
        toggleChevron($(this).parent(), 0);
    });
    $('.collapse').on('hide', function() {
        toggleChevron($(this).parent(), 1);
    });

    $('.ttip').tooltip({
        container: 'body'
    });

    $('.ttip-bottom').tooltip({
        container: 'body',
        placement: 'bottom'
    });
});

function initializeThisPolygonContent() {

    if (version === null || version === 0 || identifier === null
        || identifier === '-') return;

    $.ajax({
        url: '/activities/geojson/' + identifier,
        data: {
            'v': version
        },
        cache: false,
        success: function(data) {
            var features = geojsonFormat.read(data);
            var fLayers = [];

            if (features.length === 0) {
                // If there are no polygons, hide the entire section.
                $('#thisDealSection').hide();
            } else {
                // Add the polygon layers in the same order as the areaNames.
                for (var a in areaNames) {

                    $.each(features, function() {

                        // The name is the first (and only) attribute
                        for (var n in this.attributes) break;

                        var an = areaNames[a];
                        if ($.isArray(areaNames[a])) {
                            an = areaNames[a][0];
                        }
                        if (n !== an) {
                            if ("custom_area_names" in window) {
                                n = custom_area_names[a];
                            } else {
                                return;
                            }
                        }

                        // Add the legend
                        var t = [];
                        t.push(
                            '<li>',
                            '<div class="checkbox-modified-small">',
                            '<input class="input-top this-area-layer-checkbox" type="checkbox" value="' + n + '" id="checkboxThis' + n + '" checked="checked">',
                            '<label for="checkboxThis' + n + '"></label>',
                            '</div>',
                            '<p class="context-layers-description">',
                            '<span class="vectorLegendSymbolSmall" style="',
                                'border: 2px solid #C26464;',
                            '"><span class="vectorLegendSymbolSmallInside" style="',
                                'background-color: ' + getColor(a) + ';',
                                'opacity: 0.5;',
                                'filter: alpha(opacity=50)',
                            '"></span></span>',
                            n,
                            '</p>',
                            '</li>'
                        );
                        $('#map-this-areas-list').append(t.join(''));

                        // Add the layer
                        var styleMap = new OpenLayers.StyleMap({
                            'default': getPolygonStyle(a, '#C26464')
                        });
                        var l = new OpenLayers.Layer.Vector('this'+n, {
                            styleMap: styleMap
                        });
                        l.addFeatures([this]);
                        map.addLayer(l);

                        fLayers.push(l);
                    });
                }

                $('.this-area-layer-checkbox').click(function(e) {
                    if (e.target.value) {
                        setPolygonLayerByName(map, 'this'+e.target.value, e.target.checked);
                    }
                });

                // For the deal details, expand the options so the legend is
                // visible.
                if (readonly === true) {
                    $('.form-map-menu-toggle').click();
                }
            }

            // Zoom
            var bbox = geometryLayer.getDataExtent();
            $.each(fLayers, function() {
                bbox.extend(this.getDataExtent());
            });
            map.zoomToExtent(bbox, true);
            // Adjust zoom level so points are not zoomed in too much
            map.zoomTo(Math.min(zoomlevel, map.getZoom()-1));
        }
    });

}

function toggleMode(mode) {
    if (mode === 'add') {
        removeLayer.setVisibility(false);
        geometryLayer.setVisibility(true);
        selectCtrl.deactivate();
    } else if (mode === 'remove') {
        geometryLayer.setVisibility(false);
        removeLayer.setVisibility(true);
        removeLayer.destroyFeatures();
        var f = geometryLayer.features[0];
        if (f) {
            var mp = f.geometry.clone();
            if (mp.CLASS_NAME === 'OpenLayers.Geometry.Point') {
                var sp = mp.clone();
                mp = new OpenLayers.Geometry.MultiPoint();
                mp.addPoint(sp);
            }
            var points = mp.components;
            $.each(points, function() {
                removeLayer.addFeatures([new OpenLayers.Feature.Vector(this)]);
            });
        }
        selectCtrl.activate();
    }
}

function removeFeature(e) {
    var of = e.feature;
    var og = of.geometry;
    of.layer.removeFeatures([of]);
    var nf = geometryLayer.features[0];
    var g = nf.geometry;
    var ng = g.clone();
    $.each(ng.components, function() {
        if (this.CLASS_NAME && this.CLASS_NAME === 'OpenLayers.Geometry.Point'
            && this.equals(og)) {
            ng.removePoint(this);
            return;
        }
    });
    geometryLayer.destroyFeatures();
    geometryLayer.addFeatures([new OpenLayers.Feature.Vector(ng)]);
}

/**
 * Set a marker on the map at the given position and store the coordinates in
 * the hidden field.
 * @param {OpenLayers.LonLat} lonlat
 */
function addToMap(lonlat) {
    if (lonlat === null || lonlat.CLASS_NAME !== 'OpenLayers.LonLat') return;
    var p = new OpenLayers.Geometry.Point(lonlat.lon, lonlat.lat);
    if (editmode === 'singlepoint') {
        geometryLayer.destroyFeatures();
        geometryLayer.addFeatures([new OpenLayers.Feature.Vector(p)]);
    } else if (editmode === 'multipoints') {
        var f = geometryLayer.features[0];
        var mp;
        if (f) {
            mp = f.geometry.clone();
            if (mp.CLASS_NAME === 'OpenLayers.Geometry.Point') {
                var sp = mp.clone();
                mp = new OpenLayers.Geometry.MultiPoint();
                mp.addPoint(sp);
            }
        } else {
            mp = new OpenLayers.Geometry.MultiPoint();
        }
        mp.addPoint(p);
        geometryLayer.destroyFeatures();
        geometryLayer.addFeatures([new OpenLayers.Feature.Vector(mp)]);
    }
}

/**
 * Update the form field containing the coordinates based on the feature in the
 * geometry layer.
 * @param {OpenLayers.Event} event
 */
function updateFormCoordinates(event) {
    var feature;
    if (event && event.feature && event.feature.geometry) {
        feature = event.feature;
    } else {
        var layers = map.getLayersByName('Geometry');
        if (layers.length === 0) return;
        var geometryLayer = layers[0];
        if (!geometryLayer.features || geometryLayer.features.length !== 1
            || !geometryLayer.features[0].geometry) return;
        feature = geometryLayer.features[0];
    }
    var field = $('input[name=geometry]');
    if (field.length !== 1) return;
    if (feature.geometry.components && feature.geometry.components.length === 0) {
        $(field[0]).val('');
    } else {
        $(field[0]).val(geojsonFormat.write(feature.geometry));
    }
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
    // symbol (�) is not recognized.
    var str = escape(coordsField);
    // However, we do need to replace the spaces again do prevent regex error.
    str = str.replace(/%20/g, ' ');

    var pattern, matches;
    var latsign, longsign, d1, m1, s1, d2, m2, s2;
    var latitude, longitude, lonlat;

    if (coordsFormat == 1) {
        // 46� 57.1578 N 7� 26.1102 E
        pattern = /(\d+)[%B0\s]+(\d+\.\d+)\s*([NS])[%2C\s]+(\d+)[%B0\s]+(\d+\.\d+)\s*([WE])/i;
        matches = str.match(pattern);
        if (matches) {
            latsign = (matches[3]==='S') ? -1 : 1;
            longsign = (matches[6]==='W') ? -1 : 1;
            d1 = parseFloat(matches[1]);
            m1 = parseFloat(matches[2]);
            d2 = parseFloat(matches[4]);
            m2 = parseFloat(matches[5]);
            latitude = latsign * (d1 + (m1/60.0));
            longitude = longsign * (d2 + (m2/60.0));
            lonlat = new OpenLayers.LonLat(longitude, latitude);
        }
    } else if (coordsFormat == 2) {
        // 46� 57' 9.468" N 7� 26' 6.612" E
        pattern = /(\d+)[%B0\s]+(\d+)[%27\s]+(\d+\.\d+)[%22\s]+([NS])[%2C\s]+(\d+)[%B0\s]+(\d+)[%27\s]+(\d+\.\d+)[%22\s]+([WE])/i;
        matches = str.match(pattern);
        if (matches) {
            latsign = (matches[4]==='S') ? -1 : 1;
            longsign = (matches[8]==='W') ? -1 : 1;
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
        // N 46� 57.1578 E 7� 26.1102
        pattern = /([NS])\s*(\d+)[%B0\s]+(\d+\.\d+)[%2C\s]+([WE])\s*(\d+)[%B0\s]+(\d+\.\d+)/i;
        matches = str.match(pattern);
        if (matches) {
            latsign = (matches[1]==='S') ? -1 : 1;
            longsign = (matches[4]==='W') ? -1 : 1;
            d1 = parseFloat(matches[2]);
            m1 = parseFloat(matches[3]);
            d2 = parseFloat(matches[5]);
            m2 = parseFloat(matches[6]);
            latitude = latsign * (d1 + (m1/60.0));
            longitude = longsign * (d2 + (m2/60.0));
            lonlat = new OpenLayers.LonLat(longitude, latitude);
        }
    } else if (coordsFormat == 4) {
        // N 46� 57' 9.468" E 7� 26' 6.612"
        pattern = /([NS])\s*(\d+)[%B0\s]+(\d+)[%27\s]+(\d+\.\d+)[%22%2C\s]+([WE])\s*(\d+)[%B0\s]+(\d+)[%27\s]+(\d+\.\d+)/i;
        matches = str.match(pattern);
        if (matches) {
            latsign = (matches[1]==='S') ? -1 : 1;
            longsign = (matches[5]==='W') ? -1 : 1;
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
