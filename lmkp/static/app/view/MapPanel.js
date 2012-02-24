Ext.define('Lmkp.view.MapPanel',{
    extend: 'GeoExt.panel.Map',
    alias: ['widget.mappanel1'],

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