/**
 * Adds buttons for creating and editing polygons to the map
 *
 * @param map: a leaflet map with map options drawControl: true
 */

var initDrawPolygonControl = function (map, geometry_type) {

    // get geometry field in which drawn coordinates are written
    var $geometry = $(map.getContainer()).closest('div.taggroup').find('input[name = "geometry"]')

    var editableLayers = new L.FeatureGroup();
    map.addLayer(editableLayers);
    addExistingGeometries(map, editableLayers);

    var drawOptions = defineDrawOptions(geometry_type, editableLayers);

    // try omnivore.wkt.parse()

    var drawControl = new L.Control.Draw(drawOptions);
    map.addControl(drawControl);

    map.on(L.Draw.Event.CREATED, function (e) {
        var type = e.layerType,
            layer = e.layer;

        clearDrawnElements(map, editableLayers);
        editableLayers.addLayer(layer);

    });

    // add listener which writes the layer's coordinates to the form once the layer is created
    map.on('draw:created', function (e) {
        var layerJSON = e.layer.toGeoJSON();

        // write json to geometry field
        $geometry.val(JSON.stringify(layerJSON.geometry));

    });

    map.on('draw:deleted', function (e) {
        $geometry.val("");

    });

    map.on('draw:edited', function (e) { // Why is editable layers not defined here?
        var layers = e.layers._layers; // layers is a dictionary of edited layers
        var layer;
        // get layer from dictionary (layers should only have one key)
        for (var key in layers){
            layer = layers[key];
        }

        var layerJSON = layer.toGeoJSON();

        // set polygon value
        $geometry.val(JSON.stringify(layerJSON.geometry));

        // TODO: why does this not affect geometry field in html???
    });


    // TODO: if the layer is edited, the coordinates in the geometry field have to be adjusted!!
}

/**
 *  Create layer form coordinates saved in the geometry field.
 *  https://github.com/Leaflet/Leaflet.draw/issues/398
 */
function addExistingGeometries(map, editableLayers) {
    var $geometryField = $(map.getContainer()).closest('div.taggroup').find('input[name = "geometry"]')
    var geometryVal = $geometryField.val(); // string

    if (geometryVal !== "" && geometryVal !== null) {   // check for empty geometries
        var geometryJSON = JSON.parse(geometryVal);

        if (geometryJSON.type == "Point") {
            var coord = geometryJSON.coordinates;
            var coordLatLon = coord.reverse();
            editableLayers.addLayer(L.marker(coordLatLon));
            zoomToDealLocation(map, coordLatLon);
        }
        if (geometryJSON.type == "Polygon") {
            var coordinatesLongLat = geometryJSON.coordinates[0];
            var coordinatesLatLong = changeToLatLon(coordinatesLongLat);
            var polygonLayer = L.polygon(coordinatesLatLong);      // this must't be a layer of type L.geoJSON
            editableLayers.addLayer(polygonLayer);
        }
    }
}

/**
 * Defines draw and edit functionality of draw control. Defines which options are displayed in the draw
 * toolbar, depending on geometry_type
 *
 * @param geometry_type: 'point' or 'polygon'
 * @param editableLayers: the layers which can be edited with the edit toolbar
 * @return dictionary with draw options
 */
function defineDrawOptions(geometry_type, editableLayers) {

    var drawOptions;

    if (geometry_type === 'point') {
        var MyCustomMarker = L.Icon.extend({
            options: {
                shadowUrl: null,
                iconSize: new L.Point(24, 40),
                iconUrl: '/static/css/images/marker-icon-2x.png'  // todo: find a way to remove activities in url
            }
        });

        drawOptions = {
            position: 'topright',
            // draw options
            draw: {
                marker: {
                    icon: new MyCustomMarker()
                },
                circle: false,
                rectangle: false,
                polygon: false,
                polyline: false,
                circlemarker: false
            },
            // edit options
            edit: {
                featureGroup: editableLayers,
                remove: true
            }
        };
    }
    if (geometry_type === 'polygon') {
        drawOptions = {
            position: 'topright',
            draw: {
                polygon: {
                    allowIntersection: false, // Restricts shapes to simple polygons
                    drawError: {
                        color: '#e1e100', // Color the shape will turn when intersects
                        message: '<strong>Oh snap!<strong> you can\'t draw that!' // Message that will show when intersect
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
            },
            edit: {
                featureGroup: editableLayers,
                remove: true
            }
        };
    }

    return drawOptions;
}

// removes all layers within map
function clearDrawnElements(map, editableLayers) {
    for (var key in editableLayers._layers) { // iterate over each layer
        var layer = editableLayers._layers[key];
        editableLayers.removeLayer(layer);
    }
};

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

// TODO: move this to base.js
function zoomToDealLocation(map, coordLatLong) {
    var lat = coordLatLong[0];
    var long = coordLatLong[1];
    map.setView([lat, long], 8);
}