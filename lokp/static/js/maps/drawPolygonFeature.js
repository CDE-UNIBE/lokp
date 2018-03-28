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

    var drawOptions = defineDrawOptions(geometry_type, editableLayers);

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

    map.on('draw:edited', function (e, editableLayers) { // Why is editable layers not visible here?
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

    addExistingGeometries(map, editableLayers)

}

function addExistingGeometries(map, editableLayers) {
    var $geometryField = $(map.getContainer()).closest('div.taggroup').find('input[name = "geometry"]')
    var geometryVal = $geometryField.val(); // string

    if (geometryVal !== "" && geometryVal !== null) {   // check for empty geometries
        var geometryJSON = JSON.parse(geometryVal);

        if (geometryJSON.type == "Point") {
            var coord = geometryJSON.coordinates;
            var coordLatLon = coord.reverse();
            editableLayers.addLayer(L.marker(coordLatLon));
        }
        if (geometryJSON.type == "Polygon") {
            var geoJsonLayer = L.geoJSON(geometryJSON)
            editableLayers.addLayer(geoJsonLayer);
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
                iconAnchor: new L.Point(12, 12),
                iconSize: new L.Point(24, 24),
                iconUrl: 'static/css/images/marker-icon-2x.png'  // todo: find a way to remove activities in url
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