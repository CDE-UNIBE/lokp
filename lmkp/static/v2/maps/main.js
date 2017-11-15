/**
 * Necessary variables with translated text for this file (must be defined and
 * translated in template):
 * tForDeals
 * tForInvestor
 * tForInvestors
 * tForLegend
 * tForLegendforcontextlayer
 * tForLoading
 * tForLoadingdetails
 * tForMoredeals
 * tForNodealselected
 * tForSelecteddeals

 *
 *
 * For Map Content (Activities)
 * mapValues
 * mapCriteria
 * aKeys
 * shKeys
 *
 * Translation:
 * tForDealsGroupedBy
 */

$(document).ready(function() {

    /** Settings **/
    pointsCluster = true;
    pointsVisible = true;
    mapInteractive = true;
    contextLegendInformation = true;
    polygonLoadOnStart = false;

    // Collect any active filters (both A and SH)
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for (var i = 0; i < hashes.length; i++) {
        if (hashes[i].lastIndexOf('a__', 0) === 0 || hashes[i].lastIndexOf('sh__', 0) === 0) {
            mapFilterParams.push(hashes[i]);
        }
    }

    /**
     * Map and layers
     */
    var layers = getBaseLayers();
    map = new OpenLayers.Map('googleMapFull', {
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
        layers: layers,
        eventListeners: {
            'moveend': storeMapExtent
        }
    });
    initializeMapContent();
    initializeContextLayers();
    initializePolygonLayers();

    // Check if a location cookie is set. If yes, center the map to this location.
    // If no cookie is set, zoom the map to the extent of the current profile
    var location = $.cookie("_LOCATION_");
    if (location) {
        var arr = location.split(',');
        if (arr.length === 4) {
            var extent = new OpenLayers.Bounds(arr);
            map.zoomToExtent(extent, true);
        }
    } else {
        var f = new OpenLayers.Format.GeoJSON();
        // Variable profilePolygon is a GeoJSON geometry
        var profileExtent = f.read(profilePolygon, "Geometry");
        if (profileExtent) {
            // Reproject the extent to spherical mercator projection and zoom the map to its extent
            map.zoomToExtent(profileExtent.transform(geographicProjection, sphericalMercatorProjection).getBounds(), true);
        } else {
            map.zoomToMaxExtent();
        }
    }

    /**
     * Map Events
     */
    initializeBaseLayerControl();
    initializeContextLayerControl();
    initializePolygonLayerControl();
    initializeMapSearch();

    /**
     * GUI Events: Legend
     */

    // Deals up/down
    var mapDealsCounter = 1;
    $('.map-deals').click(function() {
        $('.map-deals-content').slideToggle();
        toggleChevron(this, mapDealsCounter++);
    });

    // Base-layers up/down
    var baseLayerCounter = 0;
    $('.base-layers').click(function() {
        $('.base-layers-content').slideToggle();
        toggleChevron(this, baseLayerCounter++);
    });

    // Context-layers up/down
    var contextLayerCounter = 0;
    $('.context-layers').click(function() {
        $('.context-layers-content').slideToggle();
        toggleChevron(this, contextLayerCounter++);
    });

    // Whole map layers up/down
    var mapLayersCounter = 0;
    $('#map-menu-button').click(function() {
        $('#map-menu-container').slideToggle();
        toggleChevron(this, mapLayersCounter++, 'up');
    });

    $(document).ready(function(){
      if ($(window).width() >= 979){
        $('#map-menu-container').slideToggle();
        $('#map-menu-button-container').hide();
      }
    });

    $(window).resize(function(){
      if ($(window).width() >= 979){
        $('#map-menu-container').show();
        $('#map-menu-button-container').hide();
      }
      if ($(window).width() <= 979){
        $('#map-menu-container').hide();
        $('#map-menu-button-container').show();
      }
    });
});


/**
 * Function to show the legend of a context layer in a modal window.
 *
 * @param {String} layerName
 * @returns {Boolean} False
 */
function showContextLegend(layerName) {

    // Find the layer in the list of available context layers
    var layer = null;
    $.each(contextLayers, function() {
        if (this.name === layerName) {
            layer = this;
        }
    });
    if (layer === null) return false;

    // Prepare URL of legend image
    var imgParams = {
        request: 'GetLegendGraphic',
        service: layer.params.SERVICE,
        version: layer.params.VERSION,
        layer: encodeURI(layer.params.LAYERS),
        style: layer.params.STYLES,
        format: 'image/png',
        width: 25,
        height: 25,
        legend_options: 'forceLabels:1;fontAntiAliasing:1;fontName:Nimbus Sans L Regular;'
    };
    var imgUrl = layer.url + '?' + decodeURI($.param(imgParams));

    // Set the content: Image is hidden first while loading indicator is shown
    //$('#mapModalHeader').html(tForLegend);
    $('#mapModalBody').html(
        '<div id="contextLegendImgLoading" style="text-align: center;">' +
            '<img src="/static/img/ajax-loader-green.gif" alt="' + tForLoading + '" height="55" width="54">' +
        '</div>' +
        '<div id="contextLegendContent" class="hide">' +
            '<h6 class="legend-modal-title">' + tForLegendforcontextlayer + ' ' + layerName + '</h6>' +
            '<div id="contextLegendAbstract"></div>' +
            '<img id="contextLegendImg" src="' + imgUrl + '">' +
        '</div>');

    // Show the model window
    $('#mapModal').openModal();

    // Once the image is loaded, hide the loading indicator and show the image
    /*$('#contextLegendImg').load(function() {
        $('#contextLegendContent').removeClass('hide');
        $('#contextLegendImgLoading').hide();
    });*/

    var abstract = layer.abstract;
    if (abstract !== undefined) {
        // Abstract was defined in YML, use this one
        setContextLegendContent(abstract);
        return false;
    }

    var getCapabilitiesRequest = layer.url + '?' + $.param({
        request: 'GetCapabilities',
        namespace: 'lo'
    });
    $.get("/proxy", {
        url: getCapabilitiesRequest
    },
    function(data){
        var xmlDoc = $.parseXML(data);
        $xml = $( xmlDoc );
        $xml.find("Layer[queryable='1']").each(function(){
            $layer = $( this );
            if($layer.find("Name").first().text() === layer.params.LAYERS
                || $layer.find("Name").first().text() === layer.params.LAYERS.split(":")[1]){
                var layerAbstract = $layer.find("Abstract").first().text();
                setContextLegendContent(layerAbstract);
                return false;
            }
        });
    });
    return false;
}

function setContextLegendContent(content) {
    $('#contextLegendAbstract').html(content);
    // Assuming to load and parse the GetCapabilites documents takes
    // longer than the image, the "Loading ..." text is hidden and the
    // #contextLegendContent div is shown as soon as the Ajax request
    // has successfully finished.
    $('#contextLegendContent').removeClass('hide');
    $('#contextLegendImgLoading').hide();
}
