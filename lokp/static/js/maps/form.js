/**
 * Functions for the main map.
 */


/*
$(document).ready(function() {
    // Only one map is displayed (in #googleMapFull), but using this as a PoC
    // which would allow creating multiple maps on same page.
    ['map1'].forEach(function(mapId) {
        createFormMap(mapId, {
            pointsVisible: true,
            pointsCluster: true
        });
    });
});
*/

function createFormMap(mapId, options) {

    var baseLayers = getBaseLayers();
    var activeBaseLayer = Object.values(baseLayers)[0];
    var map = L.map(mapId, {
        layers: activeBaseLayer,  // Initially only add first layer
        drawControl: true           // enables display of draw toolbar
    });
    map.on('moveend', function(e) {
        $.cookie('_LOCATION_', map.getBounds().toBBoxString(), {expires: 7});
    });



    map.on('click', function(e){
        var $geometry = $(this.getContainer()).closest('div.taggroup').find('input[name = "geometry"]').val(1);
        console.log($geometry);
    });

    // Initial map extent
    var initialExtent = L.geoJSON(window.mapVariables.profile_polygon).getBounds();
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

    // Disable dragging of the map for the floating buttons
    var ctrl = L.DomUtil.get('map-floating-buttons-' + mapId);
    if (ctrl) {
        ctrl.addEventListener('mouseover', function() {
            map.dragging.disable();
        });
        ctrl.addEventListener('mouseout', function() {
            map.dragging.enable();
        });
    }

    // Hide loading overlay
    $('.map-loader[data-map-id="' + mapId + '"]').hide();

    if (typeof window.lokp_maps === 'undefined') {
        window.lokp_maps = {};
    }
    window.lokp_maps[mapId] = {
        map: map,
        baseLayers: baseLayers,
        contextLayers: getContextLayers(mapId, window.mapVariables.context_layers),
        polygonLayers: {},
        // Keep track of the currently active base layer so it can be changed
        // programmatically
        activeBaseLayer: activeBaseLayer,
        activeMapMarker: null,
        // Initial map variables
        mapVariables: window.mapVariables,
        options: options
    };

    initBaseLayerControl();
    initMapContent(map);
    initPolygonLayers(mapId, window.mapVariables.polygon_keys);
    initContextLayerControl();
    initMapSearch(mapId);
    initDrawPolygonControl(map);
}


