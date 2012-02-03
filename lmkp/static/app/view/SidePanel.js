Ext.define('LmkpP.view.SidePanel' ,{
    extend: 'Ext.tab.Panel',
    alias : 'widget.sidepanel',

    initComponent: function() {
        this.items = [{
            width: 200,
            xtype: 'layerslist'
        },{
            html: 'Add new event',
            title: 'Add new',
            xtype: 'panel'
        },{
            html: 'Filters',
            title: 'Filters',
            xtype: 'panel'
        }]
        this.callParent(arguments);
    }
});