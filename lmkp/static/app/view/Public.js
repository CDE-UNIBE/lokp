Ext.define('Lmkp.view.Public' ,{
    extend: 'Ext.panel.Panel',
    alias : ['widget.lo_publicpanel'],

    border: false,
    layout: 'border',

    items: [{
        contentEl: 'header-div',
        height: 80,
        region: 'north',
        xtype: 'panel'
    },{
        region: 'center',
        html: 'public <i>panel</i>',
        xtype: 'panel'
    }],

    tbar: {
        xtype: 'lo_logintoolbar'
    }
});