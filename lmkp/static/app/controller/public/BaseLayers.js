Ext.define('Lmkp.controller.public.BaseLayers', {
    extend: 'Ext.app.Controller',

    views: [
    'public.BaseLayers'
    ],

    init: function() {
        this.control({
            'lo_baselayers menucheckitem':{
                checkchange: this.onMenuCheckChange
            }
        });
    },

    onMenuCheckChange: function(item, checked, eOpts){
        if(checked){
            var map = item.layer.map;
            map.setBaseLayer(item.layer);
        }
    }

});