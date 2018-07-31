/**
 * Initialize controls, buttons etc. to draw on the map. Loads initial features.
 * @param {object} mapOptions
 */
function initDrawControl(mapOptions) {
    var map = mapOptions.map;
    var geometryType = mapOptions.options.geometry_type['geometry_type'];
    var drawMultipleFeatures = mapOptions.options.draw_multiple_features;

    // Get initial features, store them to mapOptions and add them to the map.
    var geojsonString = getGeometryField(map).val();
    var drawnFeatures = getDrawnFeatures(geojsonString);
    mapOptions['drawnFeatures'] = drawnFeatures;
    map.addLayer(drawnFeatures);

    // Zoom to layer.
    var bounds = drawnFeatures.getBounds();
    if (bounds.isValid()) {
        if (geometryType === 'point') {
            map.setView(bounds.getCenter(), 8)
        } else {
            map.fitBounds(bounds);
        }
    }

    // Initialize the draw control and add it to the map.
    var drawOptions = getDrawControlOptions(geometryType, drawnFeatures);
    var drawControl = new L.Control.Draw(drawOptions);
    map.addControl(drawControl);

    // Events: If only single features can be drawn, remove the previous
    // features when creating a new one.
    map.on(L.Draw.Event.CREATED, function(e) {
        if (!drawMultipleFeatures) {
            // Remove existing features if only one can be drawn
            drawnFeatures.eachLayer(function(layer) {
                drawnFeatures.removeLayer(layer);
            });
        }
        drawnFeatures.addLayer(e.layer);
    });

    // After creating, editing or deleting features, update the geometry field.
    map.on('draw:created', function(e) {
        updateGeometryField(map, drawnFeatures);
    }).on('draw:edited', function(e) {
        updateGeometryField(map, drawnFeatures);
    }).on('draw:deleted', function(e) {
        updateGeometryField(map, drawnFeatures);
    });
}


/**
 * Return a FeatureGroup, either empty or containing initial features (Marker or
 * Polygon) as defined in the geojson string.
 * @param {string} geojsonString: A geojson (only the geometry).
 * @returns {L.featureGroup}
 */
function getDrawnFeatures(geojsonString) {
    var drawnFeatures = L.featureGroup();
    if (geojsonString) {
        // If a geojson was provided (by the DB), parse it and add it (as
        // editable) to the map.
        var geojson = JSON.parse(geojsonString);
        var latLngCoords;
        if (geojson.type === 'Point') {
            // Point: Add a marker.
            latLngCoords = L.GeoJSON.coordsToLatLng(geojson.coordinates);
            drawnFeatures.addLayer(L.marker(latLngCoords));
        } else if (geojson.type === 'Polygon') {
            // Polygon: Add a single polygon.
            latLngCoords = geojson.coordinates.map(function(c) {
                return L.GeoJSON.coordsToLatLngs(c);
            });
            drawnFeatures.addLayer(L.polygon(latLngCoords));
        } else if (geojson.type === 'MultiPolygon') {
            // MultiPolygon: Add each polygon separately (so they are editable
            // independently).
            geojson.coordinates.forEach(function(c1) {
                c1.forEach(function(c2) {
                    latLngCoords = L.GeoJSON.coordsToLatLngs(c2);
                    drawnFeatures.addLayer(L.polygon(latLngCoords));
                })
            });
        }
    }
    return drawnFeatures;
}


/**
 * Update the hidden geometry field of the form based on the features currently
 * drawn on the map.
 * @param {L.map} map: The current map.
 * @param {L.featureGroup} features: The features currently drawn on the map.
 */
function updateGeometryField(map, features) {
    // Extract only the geometries of the geojson
    var geomList = features.toGeoJSON().features.map(function(f) {
        return f.geometry;
    });
    if (geomList.length === 0) {
        writeGeometry(map, null);
    }
    else if (geomList.length === 1) {
        writeGeometry(map, geomList[0]);
    } else {
        // Each polygon is on a separate layer. Smash them together and create a
        // new MultiPolygon feature.
        var newGeometry = {
            type: 'MultiPolygon',
            coordinates: geomList.map(function(g) {
                return g.coordinates;
            })
        };
        writeGeometry(map, newGeometry);
    }
}


/**
 * Write the geojson to the hidden geometry field.
 * @param {L.map} map: The current map.
 * @param {object|null} geometryJSON: The geometry JSON or null if empty.
 */
function writeGeometry(map, geometryJSON) {
    var val = (geometryJSON === null) ? '' : JSON.stringify(geometryJSON);
    getGeometryField(map).val(val);
}


/**
 * Get the hidden geometry form field relative to the current map.
 * @param {L.map} map: The current map.
 * @returns {jQuery}
 */
function getGeometryField(map) {
    return $(map.getContainer()).closest('div.taggroup').find('input[name = "geometry"]');
}


/**
 * Get draw and edit functionality of draw control. Defines which options are
 * displayed in the draw toolbar, depending on geometry_type
 *
 * @param {string} geomType: Either 'point' or 'polygon'
 * @param {L.featureGroup} drawnFeatures: The layers which can be edited with
 *        the edit toolbar
 * @returns {object} Object with draw options
 */
function getDrawControlOptions(geomType, drawnFeatures) {
    // Shared drawing options
    var drawOptions = {
        position: 'topright',
        edit: {
            featureGroup: drawnFeatures,
            remove: true
        }
    };
    if (geomType === 'point') {
        // Point
        var CustomMarker = L.Icon.extend({
            options: {
                shadowUrl: null,
                iconSize: new L.Point(24, 40),
                iconUrl: '/static/css/images/marker-icon-2x.png'
            }
        });

        drawOptions['draw'] = {
            marker: {
                icon: new CustomMarker()
            },
            circle: false,
            rectangle: false,
            polygon: false,
            polyline: false,
            circlemarker: false
        };
    }
    if (geomType === 'polygon') {
        // Polygon
        drawOptions['draw'] = {
            polygon: {
                allowIntersection: false, // Restricts shapes to simple polygons
                drawError: {
                    color: '#e1e100', // Color the shape will turn when intersects
                    message: 'you can\'t draw that!' // Message that will show when intersect
                },
                shapeOptions: {
                    color: '#bada55'
                }
            },
            marker: false,
            circle: false,
            rectangle: false,
            polyline: false,
            circlemarker: false
        };
    }
    return drawOptions;
}
