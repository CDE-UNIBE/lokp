Ext.define('Lmkp.view.Main' ,{
    extend: 'Ext.panel.Panel',
    alias : ['widget.main'],
    
    layout: 'border',
    defaults: {
        collapsible: true,
        split: true
    },

    initComponent: function() {
        this.items = [{
            collapsible: false,
            region: 'west',
            xtype: 'filterPanel',
            width: 300
        },{
            collapsible: false,
            region: 'center',
            frame: false,
            xtype: 'mappanel'
        }]
        this.callParent(arguments);
    }
});