/**
 * Static variables
 */
// Define the geographic and spherical mercator globally
var geographicProjection = new OpenLayers.Projection("EPSG:4326");
var sphericalMercatorProjection = new OpenLayers.Projection("EPSG:900913");

// Change the base map
$('.baseMapOptions').change(function(e) {
    if (e.target.value) {
        setBaseLayerByName(map, e.target.value);
    }
});

/**
 * Initialize the spatial search functionality.
 * Requires an input field with id="search" and name="q".
 */
function initializeMapSearch() {
    // Add a marker layer, which is used in the location search
    var markers = new OpenLayers.Layer.Markers( "Markers" );
    map.addLayer(markers);
    var rows = new Array();
    $("#search").typeahead({
        items: 5,
        minLength: 3,
        source: function( query , process ) {
            $.get("/search", {
                q: query,
                epsg: 900913
            },
            function(response) {
                rows = new Array();
                if(response.success){
                    for(var i = 0; i < response.data.length; i++){
                        var row = response.data[i];
                        rows.push(row);
                    }
                }

                var results = $.map(rows, function(row) {
                    return row.name;
                });

                process(results);
            } );
        },
        updater: function(item){
            var loc = new Array();
            $.each(rows, function(row){
                if(rows[row].name == item){
                    loc.push(rows[row])
                }
            });

            var selectedLocation = loc[0];
            var pos = new OpenLayers.LonLat(selectedLocation.geometry.coordinates[0], selectedLocation.geometry.coordinates[1]);

            markers.clearMarkers();
            map.setCenter(pos, 14);

            var size = new OpenLayers.Size(27,27);
            var offset = new OpenLayers.Pixel(-(size.w/2), -(size.h/2));
            var icon = new OpenLayers.Icon('/static/img/glyphicons_185_screenshot.png', size, offset);
            var m = new OpenLayers.Marker(pos, icon);
            m.events.register('click', m, function(event) {
                markers.removeMarker(m);
            });
            markers.addMarker(m);

            return loc[0].name;
        }
    }).click(function() {
        $(this).select();
    });
}

/**
 * Return the base layers of the map.
 */
function getBaseLayers() {
    var layers = [new OpenLayers.Layer.OSM("streetMap", [
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
        })];
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
    return layers;
}

/**
 * Set a base layer based on its name if it exists.
 */
function setBaseLayerByName(map, name) {
    var l = map.getLayersByName(name);
    if (l.length > 0) {
        map.setBaseLayer(l[0]);
    }
}

/**
 * Set a context layer based on its name if it exists.
 */
function setContextLayerByName(map, name, checked) {
    var l = map.getLayersByName(name);
    if (l.length > 0) {
        l[0].setVisibility(checked);
    }
}