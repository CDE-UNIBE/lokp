Ext.define('Lmkp.view.moderator.Outer' ,{
    extend: 'Ext.panel.Panel',
    alias : ['widget.lo_moderatorouterpanel'],

    requires: [
    'Lmkp.view.moderator.Main'
    ],

    border: false,
    layout: 'border',

    items: [{
        contentEl: 'header-div',
        height: 80,
        region: 'north',
        xtype: 'panel'
    },{
        region: 'center',
        xtype: 'main'
    }],

    tbar: {
        xtype: 'lo_logintoolbar'
    }
});