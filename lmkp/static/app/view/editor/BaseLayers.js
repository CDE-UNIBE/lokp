Ext.define('Lmkp.view.editor.BaseLayers',{
    extend: 'Ext.menu.Menu',
    alias: ['widget.lo_baselayers'],

    requires: [
    'Lmkp.view.editor.LayerCheckItem'
    ],

    config: {
        baseLayers: [],
        map: null
    },

    initComponent: function(){

        this.layers = this.createLayers();

        var items = [];

        for(var i=0; i < this.layers.length; i++) {
            this.map.addLayer(this.layers[i]);
            var checked = (i==0) ? true : false;
            items.push({
                checked: checked,
                group: 'baselayers',
                layer: this.layers[i],
                text: this.layers[i].name,
                xtype: 'lo_layercheckitem'
            });
            if(i==0) {
                this.map.setBaseLayer(this.layers[i]);
            }
        }

        this.items = items;

        this.callParent(arguments);
    },

    createLayers: function(){
        var layers = [
        new OpenLayers.Layer.OSM('Street Map', [
            "http://otile1.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg",
            "http://otile2.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg",
            "http://otile3.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg",
            "http://otile4.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg"
            ],{
                attribution: "<p>Tiles Courtesy of <a href=\"http://www.mapquest.com/\" target=\"_blank\">MapQuest</a> <img src=\"http://developer.mapquest.com/content/osm/mq_logo.png\"></p>",
                isBaseLayer: true,
                sphericalMercator: true,
                projection: new OpenLayers.Projection("EPSG:900913")
            }),
        new OpenLayers.Layer.OSM('Open Aerial', [
            "http://oatile1.mqcdn.com/tiles/1.0.0/sat/${z}/${x}/${y}.jpg",
            "http://oatile2.mqcdn.com/tiles/1.0.0/sat/${z}/${x}/${y}.jpg",
            "http://oatile3.mqcdn.com/tiles/1.0.0/sat/${z}/${x}/${y}.jpg",
            "http://oatile4.mqcdn.com/tiles/1.0.0/sat/${z}/${x}/${y}.jpg"
            ],{
                attribution: "<p>Tiles Courtesy of <a href=\"http://www.mapquest.com/\" target=\"_blank\">MapQuest</a> <img src=\"http://developer.mapquest.com/content/osm/mq_logo.png\"></p>",
                isBaseLayer: true,
                sphericalMercator: true,
                projection: new OpenLayers.Projection("EPSG:900913")
            })
        ];

        return layers;
    }

});