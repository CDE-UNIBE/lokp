Ext.define('Lmkp.view.moderator.Outer' ,{
    extend: 'Lmkp.view.Panel',
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
        xtype: 'lo_panel'
    },{
        region: 'center',
        xtype: 'lo_moderatormainpanel'
    }],

    tbar: {
        xtype: 'lo_logintoolbar'
    }
});