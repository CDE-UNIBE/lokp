Ext.define('Lmkp.view.administrator.Outer' ,{
    extend: 'Lmkp.view.Panel',
    alias : ['widget.lo_administratorouterpanel'],

    requires: [
    'Lmkp.view.administrator.Main',
    'Lmkp.view.login.Toolbar'
    ],

    border: false,
    layout: 'border',

    items: [{
        contentEl: 'header-div',
        height: 80,
        region: 'north',
        xtype: 'lo_panel'
    },{
        region: 'center',
        xtype: 'lo_administratormainpanel'
    }],

    tbar: {
        xtype: 'lo_logintoolbar'
    }
});