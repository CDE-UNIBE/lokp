Ext.define('Lmkp.view.MapPanel',{
    extend: 'GeoExt.panel.Map',
    alias: ['widget.mappanel'],

    requires: [
    'GeoExt.Action'
    ],

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
        new OpenLayers.Layer.OSM('mapnik'),
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
            }
        })
        ],
        projection: this.sphericalMercatorProjection
    },

    sphericalMercatorProjection: new OpenLayers.Projection("EPSG:900913"),

    // Add an empty toolbar to add the GeoExt actions in the Map controller
    tbar: [],

    /*tbar: [{
        iconCls: 'pan-button',
        toggleGroup: 'map-controls'
    },'->',{
        fieldLabel: 'Change Map Layer',
        store: [
        'mapnik',
        'osmarenderer'
        ],
        queryMode: 'local',
        xtype: 'combobox'
    }],*/

    zoom: 2,

    getVectorLayer: function(){
        return this.getMap().getLayersByName('vector')[0];
    },

    getBaseLayer: function(){
        return this.getMap().getLayersByName('mapnik')[0];
    }

})
