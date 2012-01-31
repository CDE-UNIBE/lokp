Ext.define('LMKP.view.MapPanel',{
    extend: 'GeoExt.panel.Map',
    alias: ['widget.mappanel'],

    config: {
        map: {}
    },

    map: {
        layers: [new OpenLayers.Layer.OSM('Mapnik')]
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