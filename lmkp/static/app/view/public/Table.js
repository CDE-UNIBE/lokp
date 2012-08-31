Ext.define('Lmkp.view.public.Table' ,{
    extend: 'Ext.container.Container',
    alias : ['widget.lo_publictablepanel'],

    requires: [
    ],

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    items: [{
        flex: 0.5,
        border: 0,
        frame: false,
        xtype: 'lo_editoractivitytablepanel'
    },{
        flex: 0.5,
        xtype: 'lo_editorstakeholdertablepanel'
    }]

});
