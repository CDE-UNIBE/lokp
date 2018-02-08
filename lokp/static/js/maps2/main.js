/**
 * Functions for the main map.
 */

$(document).ready(function() {
    // Only one map is displayed (in #googleMapFull), but using this as a PoC
    // which would allow creating multiple maps on same page.
    ['googleMapFull'].forEach(function(mapId) {
        createMainMap(mapId, {
            pointsVisible: true,
            pointsCluster: true
        });
    });
});


function createMainMap(mapId, options) {
    var baseLayers = getBaseLayers();
    var activeBaseLayer = Object.values(baseLayers)[0];
    var map = L.map(mapId, {
        layers: activeBaseLayer  // Initially only add first layer
    });
    map.on('moveend', function(e) {
        $.cookie('_LOCATION_', map.getBounds().toBBoxString(), {expires: 7});
    });
    
    // Initial map extent
    var initialExtent = L.geoJSON(window.mapVariables.map_profile_poly).getBounds();   // mapVariables defined in map.py (get_map_variables returns js)
    var locationCookie = $.cookie('_LOCATION_');
    if (locationCookie) {
        // If a valid cookie is set, use this as extent
        var parts = locationCookie.split(',');
        if (parts.length === 4) {
            initialExtent = L.latLngBounds(
                L.latLng(parts[1], parts[0]),
                L.latLng(parts[3], parts[2]));
        }
    }
    map.fitBounds(initialExtent);

    if (typeof window.lokp_maps === 'undefined') {
        window.lokp_maps = {};
    }
    window.lokp_maps[mapId] = {
        map: map,
        baseLayers: baseLayers,
        // Keep track of the currently active base layer so it can be changed
        // programmatically
        activeBaseLayer: activeBaseLayer,
        // Initial map variables
        mapVariables: window.mapVariables,
        options: options
    };

    initBaseLayerControl();
    initMapContent(map);

    // TODO
    // initContextLayers(); + control
    // initPolygonLayers(); + control
    // initMapSearch();
}
