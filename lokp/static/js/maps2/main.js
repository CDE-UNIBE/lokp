/**
 * Functions for the main map.
 */

$(document).ready(function() {
    createMainMap('main-map-id', {
        // Whether points are initially visible or not
        pointsVisible: true,
        // Whether points are clustered or not
        pointsCluster: true,
        // ID of div to show details in. If not specified, no details will be shown.
        detailPanelId: 'tab1'
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
}
