Ext.define('Lmkp.view.SidePanel' ,{
    extend: 'Ext.panel.Panel',
    alias : ['widget.sidepanel'],

    layout: 'border',

    items: [{
        region: 'center',
        xtype: 'filterPanel'
    }]
});