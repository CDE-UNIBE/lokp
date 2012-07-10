Ext.define('Lmkp.view.Table' ,{
    extend: 'Ext.tab.Panel',
    alias : ['widget.lo_tablepanel'],

    items: [{
        xtype: 'filterPanel'
    },{
        xtype: 'stakeholderpanel'
    }],

    title: 'Table View'
});