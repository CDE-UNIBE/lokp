Ext.define('Lmkp.view.editor.GxMap',{
    extend: 'GeoExt.panel.Map',
    alias: ['widget.lo_editorgxmappanel'],

    requires: [
    'GeoExt.Action'
    ],

    border: false,
    frame: false,
    center: new OpenLayers.LonLat(0,0),

    config: {
        map: {}
    },

    layout: 'fit',

    geographicProjection: new OpenLayers.Projection("EPSG:4326"),

    map: {
        displayProjection: this.geographicProjection,
        controls: [
        new OpenLayers.Control.Navigation()
        ],
        layers: [
        new OpenLayers.Layer.OSM('mapnik', null, {
            sphericalMercator: true,
            projection: new OpenLayers.Projection("EPSG:900913")
        }),
        new OpenLayers.Layer.WMS('Activities',
            'http://localhost:8080/geoserver/lo/wms',{
                layers: 'activities',
                transparent: true,
                format: 'image/png8',
                epsg: 900913
            },{
                isBaseLayer: false,
                sphericalMercator: true,
                maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34,
                    20037508.34, 20037508.34)
            }),
        new OpenLayers.Layer.Vector('vector',{
            isBaseLayer: false,
            // Add an event listener to reproject all features from geographic
            // projection to the spherical Mercator projection.
            // Thus: the layer expect that all features are in EPSG:4326!
            eventListeners: {
                "beforefeatureadded": function(feature){
                    var geom = feature.feature.geometry;
                    // Reproject the feature's geometry from geographic coordinates
                    // to spherical Mercator coordinates.
                    geom.transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));
                }
            },
            styleMap: new OpenLayers.StyleMap({
                "default": new OpenLayers.Style({}, {
                    rules: [
                    new OpenLayers.Rule({
                        title: "list",
                        filter: new OpenLayers.Filter.Comparison({
                            property: 'list',
                            type: OpenLayers.Filter.Comparison.EQUAL_TO,
                            value: '1'
                        }),
                        symbolizer: {
                            graphicName: "star",
                            pointRadius: 7,
                            fillColor: "#bd0026",
                            fillOpacity: 0.8,
                            strokeColor: "#bd0026",
                            strokeWidth: 1
                        }
                    }),
                    new OpenLayers.Rule({
                        elseFilter: true,
                        symbolizer: {
                            graphicName: "circle",
                            pointRadius: 7,
                            fillColor: "#ff0000",
                            fillOpacity: 0.8,
                            strokeColor: "#bd0026",
                            strokeWidth: 1
                        }
                    })]
                })
            })
        })
        ],
        projection: this.sphericalMercatorProjection
    },

    sphericalMercatorProjection: new OpenLayers.Projection("EPSG:900913"),

    // Add an empty toolbar to add the GeoExt actions in the Map controller
    tbar: {},

    zoom: 2,

    getVectorLayer: function(){
        return this.getMap().getLayersByName('vector')[0];
    },

    getBaseLayer: function(){
        return this.getMap().getLayersByName('mapnik')[0];
    },

    getActivitiesLayer: function(){
        return this.getMap().getLayersByName('Activities')[0];
    }

})
