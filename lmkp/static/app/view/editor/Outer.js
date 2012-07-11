Ext.define('Lmkp.view.editor.Outer' ,{
    extend: 'Ext.panel.Panel',
    alias : ['widget.lo_editorouterpanel'],

    requires: [
        'Lmkp.view.login.Toolbar',
        'Lmkp.view.editor.Main'
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
        xtype: 'lo_editormainpanel'
    }],

    tbar: {
        xtype: 'lo_logintoolbar'
    }
});