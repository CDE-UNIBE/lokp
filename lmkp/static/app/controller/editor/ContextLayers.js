Ext.define('Lmkp.controller.editor.ContextLayers', {
    extend: 'Ext.app.Controller',

    views: [
    'editor.ContextLayers'
    ],

    init: function() {
        this.control({
            'lo_contextlayers lo_layercheckitem':{
                checkchange: this.onMenuCheckChange
            }
        });
    },

    onMenuCheckChange: function(item, checked, eOpts){
        item.layer.setVisibility(checked);
    }

});