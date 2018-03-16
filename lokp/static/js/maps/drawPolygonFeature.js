/**
 * Adds buttons for creating and editing polygons to the map
 *
 * @param map: a leaflet map with map options drawControl: true
 */

var initDrawPolygonControl = function (map) {

    var editableLayers = new L.FeatureGroup();
    map.addLayer(editableLayers);

    var MyCustomMarker = L.Icon.extend({
        options: {
            shadowUrl: null,
            iconAnchor: new L.Point(12, 12),
            iconSize: new L.Point(24, 24),
            iconUrl: 'static/css/images/marker-icon-2x.png'
        }
    });

    // configure options of draw control
    var options = {
        position: 'topright',
        draw: {
            polyline: {
                shapeOptions: {
                    color: '#f357a1',
                    weight: 10
                }
            },
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
            circle: false, // Turns off this drawing tool
            rectangle: {
                shapeOptions: {
                    clickable: false
                }
            },
            marker: {
                icon: new MyCustomMarker()
            }
        },
        edit: {
            featureGroup: editableLayers, //REQUIRED!!
            remove: true
        }
    };

    var drawControl = new L.Control.Draw(options);
    map.addControl(drawControl);

    map.on(L.Draw.Event.CREATED, function (e) {
        var type = e.layerType,
            layer = e.layer;

        if (type === 'marker') {
            layer.bindPopup('A popup!');
        }

        editableLayers.addLayer(layer);
    });

    // add listener which writes the layer's coordinates to the form once the layer is created
    map.on('draw:created', function (e) {
        var layerJSON = e.layer.toGeoJSON();

        // get geometry field
        var $geometry = $(this.getContainer()).closest('div.taggroup').find('input[name = "geometry"]')

        // write json to geometry field
        $geometry.val(JSON.stringify(layerJSON.geometry));

    });
}