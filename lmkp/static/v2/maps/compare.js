/**
 * For Map Content (Activities)
 * mapValues
 * mapCriteria
 * aKeys
 * shKeys
 *
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
    
    /** Settings **/
    pointsCluster = false;
    pointsVisible = false;
    mapInteractive = false;
    contextLegendInformation = false;
    polygonLoadOnStart = false;

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
    initializeThisPolygonContent();
    initializeMapContent();
    initializeContextLayers();
    initializePolygonLayers();

    /**
     * Map Events
     */
     initializeBaseLayerControl();
     initializeContextLayerControl();
     initializePolygonLayerControl();

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


function initializeThisPolygonContent() {
    
    if (refVersion === null || newVersion === null || identifier === null) return;
    
    var handlePolygonContent = function(f, n, a, refOrNew) {
        // Add the legend
        var t = [];
        var c = '#00CCFF';
        if (refOrNew === 'new') {
            c = '#FFCC00';
        }
        t.push(
            '<li>',
            '<div class="checkbox-modified-small">',
            '<input class="input-top ' + refOrNew + '-area-layer-checkbox" type="checkbox" value="' + n + '" id="checkbox' + refOrNew + n + '" checked="checked">',
            '<label for="checkbox' + refOrNew + n + '"></label>',
            '</div>',
            '<p class="context-layers-description">',
            '<span class="vectorLegendSymbolSmall" style="',
                'border: 2px solid ' + c + ';',
            '"><span class="vectorLegendSymbolSmallInside" style="',
                'background-color: ' + getColor(a) + ';',
                'opacity: 0.5;',
                'filter: alpha(opacity=50)',
            '"></span></span>',
            n,
            '</p>',
            '</li>'
        );
        $('#'+refOrNew+'MapLegend').append(t.join(''));

        // Add the layer
        var styleMap = new OpenLayers.StyleMap({
            'default': getPolygonStyle(a, c)
        });
        var l = new OpenLayers.Layer.Vector(refOrNew+n, {
            styleMap: styleMap
        });
        l.addFeatures([f]);
        map.addLayer(l);
        return l;
    };
    
    $.when(
        $.ajax({
            url: '/activities/geojson/' + identifier,
            data: {
                v: newVersion
            },
            cache: false
        }),
        $.ajax({
            url: '/activities/geojson/' + identifier,
            data: {
                v: refVersion
            },
            cache: false
        })
    ).done(function(a1, a2) {
        var allLayers = [];
        
        var refFeatures = geojsonFormat.read(a1[0]);
        // Add the polygon layers in the same order as the areaNames
        for (var a in areaNames) {
            $.each(refFeatures, function() {
                // The name is the first (and only) attribute
                for (var n in this.attributes) break;
                var an = areaNames[a];
                if ($.isArray(areaNames[a])) {
                    an = areaNames[a][0];
                }
                if (n !== an) return;
                allLayers.push(handlePolygonContent(this, n, a, 'new'));
            });
        }
        $('.new-area-layer-checkbox').click(function(e) {
            if (e.target.value) {
                setPolygonLayerByName(map, 'new'+e.target.value, e.target.checked);
            }
        });
        
        var newFeatures = geojsonFormat.read(a2[0]);
        // Add the polygon layers in the same order as the areaNames
        for (var a in areaNames) {
            $.each(newFeatures, function() {
                // The name is the first (and only) attribute
                for (var n in this.attributes) break;
                var an = areaNames[a];
                if ($.isArray(areaNames[a])) {
                    an = areaNames[a][0];
                }
                if (n !== an) return;
                allLayers.push(handlePolygonContent(this, n, a, 'ref'));
            });
        }
        
        $('.ref-area-layer-checkbox').click(function(e) {
            if (e.target.value) {
                setPolygonLayerByName(map, 'ref'+e.target.value, e.target.checked);
            }
        });
        
        // Zoom
        var bbox = refGeometryLayer.getDataExtent();
        bbox.extend(newGeometryLayer.getDataExtent());
        $.each(allLayers, function() {
            bbox.extend(this.getDataExtent());
        });
        map.zoomToExtent(bbox, true);
        // Adjust zoom level so points are not zoomed in too much
        map.zoomTo(Math.min(zoomlevel, map.getZoom()-1));
    });
}