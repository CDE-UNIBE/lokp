Ext.define('Lmkp.view.public.ContextLayers',{
    extend: 'Ext.menu.Menu',
    alias: ['widget.lo_contextlayers'],

    requires: [
    'Lmkp.view.public.LayerCheckItem'
    ],

    config: {
        contextLayers: [],
        map: null,
        // The parent map panel
        parent: null
    },

    initComponent: function(){

        this.layers = Lmkp.layers;

        this.map = this.parent.map

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

        // Raise the activities layer to the top of the WMS / raster layers
        this.map.raiseLayer(this.parent.activitiesLayer, ++this.layers.length);

        this.items = items;

        this.callParent(arguments);
    }

});