Ext.define('Lmkp.controller.Map',{
    extend: 'Ext.app.Controller',

    views: [
    'MapPanel'
    ],

    init: function(){
        this.control({
            'mappanel': {
                //render: this.onPanelRendered
            }
        });
    },

    onPanelRendered: function(comp){
        //comp.getMap().setCenter(new OpenLayers.LonLat(0,0),2);
        var map = comp.getMap();

        var highlightCtrl = new OpenLayers.Control.SelectFeature(comp.getVectorLayer(), {
            hover: true,
            highlightOnly: true,
            renderIntent: "temporary",
            eventListeners: {
                beforefeaturehighlighted: function(){},
                featurehighlighted: function(){},
                featureunhighlighted: function(){}
            }
        });

        var selectCtrl = new OpenLayers.Control.SelectFeature(comp.getVectorLayer(),
        {
            clickout: true
        }
        );

        map.addControl(highlightCtrl);
        map.addControl(selectCtrl);

        highlightCtrl.activate();
        selectCtrl.activate();
    }

    
})