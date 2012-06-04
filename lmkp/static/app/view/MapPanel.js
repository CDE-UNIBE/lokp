Ext.define('Lmkp.view.MapPanel',{
    extend: 'GeoExt.panel.Map',
    alias: ['widget.mappanel'],

    center: new OpenLayers.LonLat(0,0),

    config: {
        map: {}
    },

    layout: 'fit',

    geographicProjection: new OpenLayers.Projection("EPSG:4326"),

    sphericalMercatorProjection: new OpenLayers.Projection("EPSG:900913"),

    map: {
        displayProjection: this.geographicProjection,
        layers: [
        new OpenLayers.Layer.OSM('Mapnik'),
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

    tbar: {
        items: [{
            iconCls: 'zoom-in-button'
        },{
            iconCls: 'pan-button'
        },'->',{
            fieldLabel: 'Change Map Layer',
            store: [
            'mapnik',
            'osmarenderer'
            ],
            queryMode: 'local',
            xtype: 'combobox'
        }]
    },

    zoom: 2,

    getVectorLayer: function(){
        return this.getMap().getLayersByName('vector')[0];
    }

})
