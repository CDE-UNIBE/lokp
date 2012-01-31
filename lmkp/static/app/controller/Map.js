Ext.define('LMKP.controller.Map',{
    extend: Ext.app.Controller,

    views: [
    'MapPanel'
    ],

    init: function(){
        console.log('Map init');
        this.control({
            'mappanel': {
                render: this.onPanelRendered
            }
        });
    },

    onPanelRendered: function(comp){
        comp.getMap().setCenter(new OpenLayers.LonLat(0,0),2);
        console.log(comp.getMap());
    }

    
})