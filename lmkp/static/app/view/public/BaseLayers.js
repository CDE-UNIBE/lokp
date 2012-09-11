Ext.define('Lmkp.view.public.BaseLayers',{
    extend: 'Ext.menu.Menu',
    alias: ['widget.lo_baselayers'],

    requires: [
        'Lmkp.view.public.LayerCheckItem'
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
                xtype: 'menucheckitem'
            });
            if(i==0) {
                this.map.setBaseLayer(this.layers[i]);
            }
        }

        this.items = items;

        this.callParent(arguments);
    },

    createLayers: function(){
        var layers = [new OpenLayers.Layer.OSM('Street Map', [
                "http://otile1.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg",
                "http://otile2.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg",
                "http://otile3.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg",
                "http://otile4.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.jpg"
            ],{
                attribution: "<p>Tiles Courtesy of <a href=\"http://www.mapquest.com/\" target=\"_blank\">MapQuest</a> <img src=\"http://developer.mapquest.com/content/osm/mq_logo.png\"></p>",
                isBaseLayer: true,
                sphericalMercator: true,
                projection: new OpenLayers.Projection("EPSG:900913")
            })];

        // Try to get the Google Satellite layer
        try {
            layers.push(new OpenLayers.Layer.Google( "Satellite imagery", {
                type: google.maps.MapTypeId.SATELLITE,
                numZoomLevels: 22
            }));
            
            layers.push(new OpenLayers.Layer.Google( "Terrain map", {
                type: google.maps.MapTypeId.TERRAIN
            }));
        // else get backup layers that don't block the application in case there
        // is no internet connection.
        } catch(error) {
            layers.push(new OpenLayers.Layer.OSM('Satellite imagery', [
                "http://oatile1.mqcdn.com/tiles/1.0.0/sat/${z}/${x}/${y}.jpg",
                "http://oatile2.mqcdn.com/tiles/1.0.0/sat/${z}/${x}/${y}.jpg",
                "http://oatile3.mqcdn.com/tiles/1.0.0/sat/${z}/${x}/${y}.jpg",
                "http://oatile4.mqcdn.com/tiles/1.0.0/sat/${z}/${x}/${y}.jpg"
            ],{
                attribution: "<p>Tiles Courtesy of <a href=\"http://www.mapquest.com/\" target=\"_blank\">MapQuest</a> <img src=\"http://developer.mapquest.com/content/osm/mq_logo.png\"></p>",
                isBaseLayer: true,
                sphericalMercator: true,
                projection: new OpenLayers.Projection("EPSG:900913")
            }));
        }
        return layers;
    }

});