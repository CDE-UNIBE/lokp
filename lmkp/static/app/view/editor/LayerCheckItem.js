Ext.define('Lmkp.view.editor.LayerCheckItem',{
    extend: 'Ext.menu.CheckItem',
    alias: ['widget.lo_layercheckitem'],

    config: {
        layer: null
    },

    initComponent: function(){
        this.callParent(arguments);
    }

});