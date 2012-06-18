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

        // Get the toolbar
        var tbar = comp.getDockedItems('toolbar')[0];
        var map = comp.getMap();

        var dragPanAction = Ext.create('GeoExt.Action',{
            control: new OpenLayers.Control.DragPan({
                id: 'pan'
            }),
            map: map,
            iconCls: 'pan-button',
            toggleGroup: 'map-controls'
        });
        tbar.add(Ext.create('Ext.button.Button', dragPanAction));

        var zoomBoxAction = Ext.create('GeoExt.Action',{
            control: new OpenLayers.Control.ZoomBox({
                id: 'zoombox',
                type: OpenLayers.Control.TYPE_TOGGLE
            }),
            map: map,
            iconCls: 'zoom-in-button',
            toggleGroup: 'map-controls'
        });
        tbar.add(Ext.create('Ext.button.Button', zoomBoxAction));

        tbar.add(Ext.create('Ext.button.Button', {
            handler: function() {
                var selectedFeatures = new Array();
                var layers = map.getLayersByClass('OpenLayers.Layer.Vector');
                for(var i = 0; i < layers.length; i++){
                    for(var j = 0; j < layers[i].selectedFeatures.length; j++){
                        selectedFeatures.push(layers[i].selectedFeatures[j]);
                    }
                    
                }

                console.log(selectedFeatures[0]);
                var bounds = selectedFeatures[0].geometry.getBounds().clone();

                for(var i = 1; i < selectedFeatures.length; i++) {
                    bounds.extend(selectedFeatures[i].geometry.getBounds());
                }

                map.zoomToExtent(bounds);

            },
            iconCls: 'zoom-to-selected'
        }));


    }

    
})