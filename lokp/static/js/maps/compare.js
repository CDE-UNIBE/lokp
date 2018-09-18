/*****************************************************
 * Helper Methods
 ****************************************************/

function initComparisonPointMarkers(map, geometry) {
    var pointGeometries = [
        geometry.ref.geometry,
        geometry.new.geometry
    ];
    var refOrNewKey = 'ref';
    var latLngs = [];
    pointGeometries.forEach(function(geom) {
        if (geom) {
            var coords = L.GeoJSON.coordsToLatLng(geom.coordinates);
            latLngs.push(coords);
            var icon = getCustomMarker(refOrNewKey);
            L.marker(coords, {icon: icon}).addTo(map);
        }
        refOrNewKey = 'new';
    });
    return latLngs;
}


function getCustomMarker(refOrNewKey) {
    var icon = L.Icon.extend({
        options: {
            "iconUrl": "/static/css/images/marker-icon-" + refOrNewKey + ".png",
            "iconRetinaUrl": "/static/css/images/marker-icon-" + refOrNewKey + "-2x.png",
            "shadowUrl": "/static/css/images/marker-shadow.png",
            "iconSize": [25, 41],
            "iconAnchor": [12, 41],
            "popupAnchor": [1, -34],
            "tooltipAnchor": [16, -28],
            "shadowSize": [41, 41]
        }
    });
    return new icon();
}


function initComparisonPolygonLayers(map, geometry) {
    var refAreas = JSON.parse(geometry['ref'].dealAreas);
    var newAreas = JSON.parse(geometry['new'].dealAreas);
    
    var refOrNewOptions = {
        ref: {
            prefix: 'Old ',
            color: 'red'
        },
        new: {
            prefix: 'New ',
            color: 'green'
        }
    };
    var polygonLayers = {};
    var refOrNewKey = 'ref';
    var layerList = [];
    [refAreas, newAreas].forEach(function(areas) {
        for (var a in areas) {
            if (areas.hasOwnProperty(a)) {
                var layer = getFeatureGroupFromGeometry(areas[a].geometry, a);
                layer.setStyle({
                    fillColor: refOrNewOptions[refOrNewKey].color,
                    fillOpacity: 0.5
                });
                map.addLayer(layer);
                polygonLayers[refOrNewOptions[refOrNewKey].prefix + a] = layer;
                layerList.push(layer);
            }
        }
        refOrNewKey = 'new';
    });

    // add to layer control if there are layers in dictLayers
    if (!jQuery.isEmptyObject(polygonLayers)) {
        L.control.layers([], polygonLayers).addTo(map);
    }
    return layerList;
}
