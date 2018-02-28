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
            iconUrl: 'link/to/image.png'
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
        var coordinatesJSON = layerJSON.geometry.coordinates;

        // get geometry field
        var $geometry = $(this.getContainer()).closest('div.taggroup').find('input[name = "geometry"]')

        // write json to geometry field
        $geometry.val(JSON.stringify(layerJSON));

    });
    //editableLayers

    /*
    // center of the map
    var center = [-33.8650, 151.2094];

    // Create the map


    // Set up the OSM layer

    // add a marker in the given location
    L.marker(center).addTo(map);

    // Initialise the FeatureGroup to store editable layers
    var editableLayers = new L.FeatureGroup();
    map.addLayer(editableLayers);

    var drawPluginOptions = {
        position: 'topright',
        draw: {
            polygon: {
                allowIntersection: false, // Restricts shapes to simple polygons
                drawError: {
                    color: '#e1e100', // Color the shape will turn when intersects
                    message: '<strong>Oh snap!<strong> you can\'t draw that!' // Message that will show when intersect
                },
                shapeOptions: {
                    color: '#97009c'
                }
            },
            // disable toolbar item by setting it to false
            polyline: false,
            circle: false, // Turns off this drawing tool
            rectangle: false,
            marker: false,
        },
        edit: {
            featureGroup: editableLayers, //REQUIRED!!
            remove: true
        }
    };

    // Initialise the draw control and pass it the FeatureGroup of editable layers
    var drawControl = new L.Control.Draw(drawPluginOptions);
    map.addControl(drawControl);

    var editableLayers = new L.FeatureGroup();
    map.addLayer(editableLayers);

    map.on('draw:created', function (e) {
        var type = e.layerType,
            layer = e.layer;

        if (type === 'marker') {
            layer.bindPopup('A popup!');
        }

        editableLayers.addLayer(layer);
    });
    */
}