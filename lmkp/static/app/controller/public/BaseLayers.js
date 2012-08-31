Ext.define('Lmkp.controller.public.BaseLayers', {
    extend: 'Ext.app.Controller',

    views: [
    'public.BaseLayers'
    ],

    init: function() {
        this.control({
            'lo_baselayers lo_layercheckitem':{
                checkchange: this.onMenuCheckChange
            }
        });
    },

    onMenuCheckChange: function(item, checked, eOpts){
        var map = item.layer.map;
        map.setBaseLayer(item.layer);
    }

});