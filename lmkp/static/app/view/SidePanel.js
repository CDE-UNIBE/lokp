Ext.define('Lmkp.view.SidePanel' ,{
    extend: 'Ext.tab.Panel',
    alias : ['widget.sidepanel'],

    initComponent: function() {
        this.items = [{
            width: 200,
            xtype: 'layerslist'
        },{
            html: 'Add new event',
            title: 'Add new',
            xtype: 'panel'
        },{
            xtype: 'filterPanel'
        }];
        this.callParent(arguments);
    }
});