Ext.define('Lmkp.view.public.Outer' ,{
    extend: 'Ext.panel.Panel',
    alias : ['widget.lo_publicouterpanel'],

    border: false,
    layout: 'border',

    items: [{
        contentEl: 'header-div',
        height: 80,
        region: 'north',
        xtype: 'panel'
    },{
        region: 'center',
        html: 'public <i>panel</i><br/>Please login to see more ...',
        xtype: 'panel'
    }],

    tbar: {
        xtype: 'lo_logintoolbar'
    }
});