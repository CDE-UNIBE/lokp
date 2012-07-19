Ext.define('Lmkp.view.editor.Overview' ,{
    extend: 'Ext.panel.Panel',
    alias : ['widget.lo_editoroverviewpanel'],

    requires: [
    'Lmkp.view.editor.Map',
    'Lmkp.view.editor.Table'
    ],

    layout: {
        type: 'hbox',
        align: 'stretch'
    },

    items: [{
        flex: 0.5,
        items: [{
            border: 0,
            frame: false,
            title: 'Table View',
            xtype: 'lo_editortablepanel'
        },{
            border: 0,
            frame: false,
            title: 'Map View',
            xtype: 'lo_editormappanel'
        }],
        plain: true,
        xtype: 'tabpanel'
    },{
        flex: 0.5,
        xtype: 'lo_editordetailpanel'
    }]

});
