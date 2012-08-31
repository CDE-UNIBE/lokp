Ext.define('Lmkp.controller.Layers', {
    extend: 'Ext.app.Controller',
    stores: ['Layers'],
    model: ['Layer'],

    views: [
        'layers.List'
    ],
    
    /**
     * make mappanel available (can be called using this.getMappanel() because of ref: 'mappanel')
     */
    refs: [
        { ref: 'mappanel', selector: 'mappanel' },
        { ref: 'layerslist', selector: 'layerslist' }
    ],

    /**
     * At this point things haven't been rendered yet since init gets called on controllers before the launch function
     * is executed on the Application.
     */
    init: function() {
        // Do something (for example registering controls (this.control({...})) )
    },
    
    /**
     * At this point the map and therefore its layers are available. The initial layers of the map are gathered and
     * added to the store.
     */
    onLaunch: function() {
        // create empty TreeStore with empty root
        var layerRoot = Ext.create('Ext.data.TreeStore', { root: { expanded: true }}).getRootNode();
        
        // create node for base layers
        var baseLayers = Ext.create('Ext.data.TreeStore', {
            root: {
                expanded: true,
                text: 'Base Layers'
            }
        });
        var baseLayerRoot = baseLayers.getRootNode();
        
        // create node for all the other layers
        var otherLayers = Ext.create('Ext.data.TreeStore', {
            root: {
                expanded: true,
                text: 'Other Layers'
            }
        });
        var otherLayerRoot = otherLayers.getRootNode();
        
        // fetch map layers
        var mapLayers = this.getMappanel().map.layers;

        // loop through map layers and add them as children to layerRoot
        for (layer in mapLayers) {            
            var layerToAdd = [{ id: mapLayers[layer].id, text: mapLayers[layer].name, leaf: true, checked: false }];
            if (mapLayers[layer].isBaseLayer == true) {
                layerToAdd.checked = true;
                baseLayerRoot.appendChild(layerToAdd);
            } else {
                otherLayerRoot.appendChild(layerToAdd);
            }
        }
        layerRoot.appendChild(baseLayerRoot);
        layerRoot.appendChild(otherLayerRoot);
        
        /**
         * 
         * I (Lukas) removed the following code because it kept throwing error message.
         * add it again once layer stuff works.
         * 
         */
        // set layerRoot as root node of the tree.
        // this.getLayerslist().setRootNode(layerRoot);
    }
});