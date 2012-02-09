Ext.define('Lmkp.view.layers.List' ,{
    extend: 'Ext.tree.Panel',
    alias : 'widget.layerslist',
    store: 'Layers',

    html: 'Will be replace by a tab panel',
    title: 'Layers',

    /**
     * So far only used for managing display properties of the tree.
     */
    initComponent: function() {
        
        this.rootVisible = false;
        
        this.callParent(arguments);
    }
});