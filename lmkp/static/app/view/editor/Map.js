Ext.define('Lmkp.view.editor.Map',{
    extend: 'Ext.panel.Panel',
    alias: ['widget.lo_editormappanel'],

    requires: [
    'Lmkp.view.editor.GxMap',
    'Lmkp.view.editor.Detail'
    ],

    layout: {
        type: 'hbox',
        align: 'stretch'
    },

    border: false,

    frame: false,

    items: [{
        flex: 0.5,
        xtype: 'lo_editorgxmappanel'
    },{
        html: 'this <i>will</i> be the future detailpanel',
        flex: 0.5,
        xtype: 'lo_editordetailpanel'
    }]

});