var geographicProjection = new OpenLayers.Projection("EPSG:4326");
var sphericalMercatorProjection = new OpenLayers.Projection("EPSG:900913");

$(document).ready(function() {
    var layers = getBaseLayers();

    markerLayer = new OpenLayers.Layer.Markers("Points", {
        'calculateInRange': function() { return true; }
    });
    layers.push(markerLayer);

    var map = new OpenLayers.Map('googleMapNotFull', {
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

    if (bbox) {
        map.zoomToExtent(bbox, true);
    } else {
        var coordsTransformed = new OpenLayers.LonLat(coords[0], coords[1])
            .transform(geographicProjection,sphericalMercatorProjection);
        map.setCenter(coordsTransformed, zoomlevel);
    }
    if (pointIsSet) {
        markerLayer.addMarker(getMarker(coordsTransformed));
    }

    if (!readonly) {
        $('#googleMapNotFull').css('cursor', "crosshair");

        map.events.register('click', map, function(e) {
            var position = map.getLonLatFromPixel(e.xy);

            // Set a new marker on the map
            markerLayer.clearMarkers();
            markerLayer.addMarker(getMarker(position));

            // Store the new coordinates for form submission
            var coords = position.clone().transform(sphericalMercatorProjection, geographicProjection)
            var lon = $('input[name=lon]');
            if (lon && lon.length == 1) {
                $(lon[0]).val(coords.lon);
            }
            var lat = $('input[name=lat]');
            if (lat && lat.length == 1) {
                $(lat[0]).val(coords.lat);
            }
        });
    }
});

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

function getMarker(coords) {
    var size = new OpenLayers.Size(25,25);
    var offset = new OpenLayers.Pixel(-(size.w/2), -size.h);
    // Icon by: http://www.iconbeast.com
    var icon = new OpenLayers.Icon('/static/img/pin_darkred.png',size,offset);
    return new OpenLayers.Marker(coords, icon);
}