Ext.define('LMKP.view.Main' ,{
    extend: 'Ext.panel.Panel',
    alias : 'widget.main',
    layout: 'border',

    initComponent: function() {
        this.items = [{
            region: 'west',
            width: 200,
            xtype: 'sidepanel'
        },{
            html: 'main panel center',
            region: 'center',
            title: 'Map Panel',
            xtype: 'panel'
        }]
        this.callParent(arguments);
    }
});