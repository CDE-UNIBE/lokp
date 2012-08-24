Ext.define('Lmkp.controller.editor.ContextLayers', {
    extend: 'Ext.app.Controller',

    views: [
    'editor.ContextLayers'
    ],

    init: function() {
        this.control({
            'lo_contextlayers lo_layercheckitem': {
                checkchange: this.onMenuCheckChange,
                showlegend: this.onMenuShowLegend
            }
        });
    },

    onMenuCheckChange: function(item, checked, eOpts){
        item.layer.setVisibility(checked);
    },

    /**
     * Opens a new window with the legend graphic returned by the WMS service.
     */
    onMenuShowLegend: function(item, layer){

        var width = 100;

        // Construct the WMS GetLegendGraphic URL
        var imgsrc = layer.url
        + '?service=WMS&version=1.1.0&request=GetLegendGraphic&FORMAT=image/png&width=25&height=25&layer='
        + layer.params.LAYERS
        + '&style='
        + layer.params.STYLES
        Ext.create('Ext.window.Window', {
            title: layer.name,
            layout: 'fit',
            hideMode: 'display',
            items: {
                // Redo the layout after rendering to make sure the whole image
                // is shown. But not sure if this is really the final and best
                // solution... ?
                listeners: {
                    'afterrender': function(comp, eOpts){
                        comp.doLayout();
                    }
                },
                html: '<img src="' + imgsrc + '">',
                padding: 5,
                xtype: 'panel'
            }
        }).show();
    }

});