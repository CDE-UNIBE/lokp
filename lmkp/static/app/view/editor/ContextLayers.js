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

        this.layers = Lmkp.layers;

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
    }

});