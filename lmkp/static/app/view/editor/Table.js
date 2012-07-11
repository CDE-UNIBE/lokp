Ext.define('Lmkp.view.editor.Table',{
    extend: 'Ext.panel.Panel',
    alias: ['widget.lo_editortablepanel'],

    requires: [
    ],

    layout: {
        type: 'hbox',
        align: 'stretch'
    },

    border: false,

    frame: false,

    items: [{
        flex: 0.5,
        html: "test",
        xtype: 'panel'
    },{
        flex: 0.5,
        html: 'this <i>will</i> be the future detailpanel',
        xtype: 'panel'
    }]

});