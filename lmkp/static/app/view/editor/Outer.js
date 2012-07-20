Ext.define('Lmkp.view.editor.Outer' ,{
    extend: 'Ext.panel.Panel',
    alias : ['widget.lo_editorouterpanel'],

    requires: [
    'Lmkp.view.login.Toolbar',
    'Lmkp.view.editor.Overview'
    ],

    border: false,
    layout: 'border',

    items: [{
        contentEl: 'header-div',
        height: 80,
        region: 'north',
        xtype: 'panel'
    },{
        border: 0,
        frame: false,
        region: 'center',
        xtype: 'lo_editoroverviewpanel'
    }],

    tbar: {
        xtype: 'lo_logintoolbar'
    }
});