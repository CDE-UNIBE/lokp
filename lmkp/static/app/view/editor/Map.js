Ext.define('Lmkp.view.editor.Map',{
    extend: 'GeoExt.panel.Map',
    alias: ['widget.lo_editormappanel'],

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
        new OpenLayers.Layer.Vector('pointLayer',{
            isBaseLayer: false
        })],
        projection: this.sphericalMercatorProjection
    },

    sphericalMercatorProjection: new OpenLayers.Projection("EPSG:900913"),

    // Add an empty toolbar to add the GeoExt actions in the Map controller
    tbar: [],

    zoom: 2,

    getVectorLayer: function(){
        return this.getMap().getLayersByName('pointLayer')[0];
    },

    getBaseLayer: function(){
        return this.getMap().getLayersByName('mapnik')[0];
    },

    getActivitiesLayer: function(){
        return this.getMap().getLayersByName('Activities')[0];
    }

});