Ext.define('Lmkp.view.SidePanel' ,{
    extend: 'Ext.panel.Panel',
    alias : ['widget.sidepanel'],

    layout: 'fit',

    items: [{
        // region: 'center',
        xtype: 'filterPanel'
    }]
});