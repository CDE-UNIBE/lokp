Ext.define('Lmkp.view.MapPanel',{
    extend: 'GeoExt.panel.Map',
    alias: ['widget.mappanel'],

    config: {
        map: {}
    },

    layout: 'fit',

    map: {
        displayProjection: new OpenLayers.Projection("EPSG:4326"),
        layers: [
        	new OpenLayers.Layer.OSM('Mapnik')
        ],
        projection: new OpenLayers.Projection("EPSG:900913")
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
    }

})
