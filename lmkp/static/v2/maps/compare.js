/**
 * For Map Content (Activities)
 * mapValues
 * mapCriteria
 * aKeys
 * shKeys
 *
 * tForDealsGroupedBy
 * tForChangesInThisSection
 */

var geographicProjection = new OpenLayers.Projection("EPSG:4326");
var sphericalMercatorProjection = new OpenLayers.Projection("EPSG:900913");
var geojsonFormat = new OpenLayers.Format.GeoJSON({
    'internalProjection': sphericalMercatorProjection,
    'externalProjection': geographicProjection
});
var refGeometryLayer,
    newGeometryLayer;

$(document).ready(function() {

    /**
     * Map and layers
     */
    var layers = getBaseLayers();

    var refMarkerStyle = new OpenLayers.StyleMap({
        'default': OpenLayers.Util.applyDefaults({
            externalGraphic: '/static/img/pin_blue.png',
            graphicHeight: 25,
            graphicOpacity: 0.8,
            graphicYOffset: -25
        }, OpenLayers.Feature.Vector.style["default"])
    });
    refGeometryLayer = new OpenLayers.Layer.Vector('RefGeometry', {
        styleMap: refMarkerStyle
    });
    layers.push(refGeometryLayer);

    var newMarkerStyle = new OpenLayers.StyleMap({
        'default': OpenLayers.Util.applyDefaults({
            externalGraphic: '/static/img/pin_yellow.png',
            graphicHeight: 25,
            graphicOpacity: 0.8,
            graphicYOffset: -25
        }, OpenLayers.Feature.Vector.style["default"])
    });
    newGeometryLayer = new OpenLayers.Layer.Vector('NewGeometry', {
        styleMap: newMarkerStyle
    });
    layers.push(newGeometryLayer);
    
    map = new OpenLayers.Map('googleMapNotFull', {
        displayProjection: geographicProjection,
        projection: sphericalMercatorProjection,
        controls: [
            new OpenLayers.Control.Attribution(),
            new OpenLayers.Control.Navigation({
                dragPanOptions: {
                    enableKinetic: true
                }
            }),
            new OpenLayers.Control.Zoom({
                zoomInId: 'btn-zoom-in',
                zoomOutId: 'btn-zoom-out'
            })
        ],
        layers: layers
    });
    setBaseLayerByName(map, 'satelliteMap');
    initializeMapContent(false, false, false);
    initializeContextLayers();

    /**
     * Map Events
     */
     initializeBaseLayerControl();
     initializeContextLayerControl();

    $('.form-map-menu-toggle').click(function() {
        $('#form-map-menu-content').toggle();
        var m = $('.form-map-compare-menu');
        m.toggleClass('active');
        if (m.hasClass('active')) {
            $(this).button('close');
        } else {
            $(this).button('reset');
        }
        return false;
    });

    if (coordsSet === true) {
        
        var refGeometry = geometry.ref;
        var newGeometry = geometry.new;
        
        if (refGeometry.geometry) {
            refGeometryLayer.addFeatures(geojsonFormat.read(refGeometry.geometry));
            var zoomExtent = refGeometryLayer.getDataExtent();
        }
        if (newGeometry.geometry) {
            newGeometryLayer.addFeatures(geojsonFormat.read(newGeometry.geometry));
            if (!refGeometry.geometry) {
                var zoomExtent = newGeometryLayer.getDataExtent();
            } else {
                zoomExtent.extend(newGeometryLayer.getDataExtent());
            }
        }
        
        if (JSON.stringify(refGeometry) !== JSON.stringify(newGeometry)) {
            $('#form-map-compare-heading').addClass('change')
                .children('div').prepend('<i class="icon-exclamation-sign ttip pointer" data-toggle="tooltip" data-original-title="' + tForChangesInThisSection + '"></i>');
            $('#collapse-map').collapse();
        }
        
        // Zoom to the feature
        map.zoomToExtent(zoomExtent);
        // Adjust zoom level
        map.zoomTo(Math.min(zoomlevel, map.getZoom()-1));
    } else {
        if (bbox) {
            map.zoomToExtent(bbox, true);
        } else {
            map.zoomToMaxExtent();
        }
    }

    $('.ttip').tooltip({
        container: 'body'
    });

    $('.ttip-bottom').tooltip({
        container: 'body',
        placement: 'bottom'
    });

    $('#activityLayerToggle').change(function(e) {
        if (e.target.value) {
            toggleContentLayers(e.target.checked);
        }
    });
    
    $('#newLayerToggle').change(function(e) {
        newGeometryLayer.display(e.target.checked);
    });
    $('#refLayerToggle').change(function(e) {
        refGeometryLayer.display(e.target.checked);
    });
});
