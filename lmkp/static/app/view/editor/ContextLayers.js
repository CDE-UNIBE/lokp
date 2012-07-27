Ext.define('Lmkp.view.editor.ContextLayers',{
    extend: 'Ext.menu.Menu',
    alias: ['widget.lo_contextlayers'],

    requires: [
    'Lmkp.view.editor.LayerCheckItem'
    ],

    config: {
        contextLayers: [],
        map: null
    },

    initComponent: function(){

        this.layers = this.createLayers();

        var items = [];

        for(var i=0; i < this.layers.length; i++) {
            this.map.addLayer(this.layers[i]);
            items.push({
                checked: false,
                layer: this.layers[i],
                text: this.layers[i].name,
                xtype: 'lo_layercheckitem'
            });
        }

        this.items = items;

        this.callParent(arguments);
    },

    createLayers: function(){
        var layers = [
        new OpenLayers.Layer.WMS("Tabi Ocean",
            "http://www.tabi.la/geoserver/tabi/wms",
            {
                epsg: 900913,
                format: 'image/png8',
                layers: "10m_ocean",
                transparent: true
            },{
                visibility: false,
                isBaseLayer: false,
                sphericalMercator: true,
                maxExtent: new OpenLayers.Bounds(-20037508.34, -20037508.34, 20037508.34, 20037508.34),
                opacity: 0.7
            }),
        new OpenLayers.Layer.WMS("DECIDE Info Poverty",
            "http://www.decide.la/geoserver/wms",
            {
                epsg: 900913,
                format: 'image/png8',
                layers: "decide:village-polygon",
                transparent: true,
                styles: 'vrppoac26'
            },{
                visibility: false,
                isBaseLayer: false,
                sphericalMercator: true,
                maxExtent: new OpenLayers.Bounds(11063487.59, 1543945.80, 12059351.76, 2593727.60),
                opacity: 0.7
            }),
        ];

        return layers;
    }


});