/**
 * Creates a map, adds controlls to it and inserts it to a div with the same id as mapId?
 */



function createFormMap(mapId, options) {
    console.log('call createFormMap function ' + mapId);
    var baseLayers = getBaseLayers();
    var activeBaseLayer = Object.values(baseLayers)[0];
    var map = L.map(mapId, {
        layers: activeBaseLayer,  // Initially only add first layer
        drawControl: true           // enables display of draw toolbar
    });
    map.on('moveend', function(e) {
        $.cookie('_LOCATION_', map.getBounds().toBBoxString(), {expires: 7});
    });


/*
    map.on('click', function(e){
        var $geometry = $(this.getContainer()).closest('div.taggroup').find('input[name = "geometry"]').val(1);
        console.log($geometry);
    });
*/
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

    if (options.readonly !== true){
        initDrawPolygonControl(map);

        // adds the location point of the deal shown in details page to the detail's page map
        addLocationOfDeal(map, geometry); // geometry is defined in mapform.mak
        zoomToDealLocation(map, geometry);
    }

}


/*****************************************************
 * Helper Methods
 ****************************************************/

/**
 *
 * @param map           Map created by createMapForm
 * @param geometry      Polygon or Point which is added to map
 */
function addLocationOfDeal(map, geometry){
    // TODO
}


function zoomToDealLocation(map, geometry){
    // TODO
}