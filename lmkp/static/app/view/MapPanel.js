Ext.define('Lmkp.view.MapPanel',{
    extend: 'GeoExt.panel.Map',
    alias: ['widget.mappanel'],

    config: {
        map: {}
    },

    map: {
        layers: [
            new OpenLayers.Layer.OSM('Mapnik'),
            new OpenLayers.Layer.OSM('Mapnik2')
        ]
    },

    tbar: [{
        text: 'Zoom'
    },{
        text: 'Pan'
    }],

    initComponent: function(){
        console.log('MapPanel init');

        this.callParent(arguments);
    }
})