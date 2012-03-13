Ext.define('Lmkp.view.MapPanel',{
    extend: 'GeoExt.panel.Map',
    alias: ['widget.mappanel'],

    config: {
        map: {}
    },

    map: {
        displayProjection: new OpenLayers.Projection("EPSG:4326"),
        layers: [
            new OpenLayers.Layer.OSM('Mapnik'),
            new OpenLayers.Layer.OSM('Mapnik2')
        ],
        projection: new OpenLayers.Projection("EPSG:900913")
    },

    tbar: [{
        text: 'Zoom'
    },{
        text: 'Pan'
    }]

})
