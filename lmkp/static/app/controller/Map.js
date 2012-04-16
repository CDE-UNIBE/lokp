Ext.define('Lmkp.controller.Map',{
    extend: 'Ext.app.Controller',

    views: [
    'MapPanel'
    ],

    init: function(){
        this.control({
            'mappanel': {
                render: this.onPanelRendered
            }
        });
    },

    onPanelRendered: function(comp){
        comp.getMap().setCenter(new OpenLayers.LonLat(0,0),2);
    }

    
})