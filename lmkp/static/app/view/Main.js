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
            region: 'center',
            xtype: 'sidepanel',
            collapsible: false
        },{
            region: 'east',
            width: 500,
            title: 'Map Panel',
            xtype: 'mappanel'
        }]
        this.callParent(arguments);
    }
});