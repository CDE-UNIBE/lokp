Ext.define('Lmkp.view.public.Main' ,{
    extend: 'Ext.container.Container',
    alias : ['widget.lo_publicmainpanel'],

    requires: [
    'Lmkp.view.public.Map',
    'Lmkp.view.public.ActivityTable',
    'Lmkp.view.public.StakeholderTable'
    ],

    layout: {
        type: 'hbox',
        align: 'stretch'
    },

    items: [{
        flex: 0.5,
        items: [{
            border: 0,
            flex: 0.5,
            frame: false,
            title: Lmkp.ts.msg('activities-table_view'),
            xtype: 'lo_publicactivitytablepanel'
        }, {
            border: 0,
            flex: 0.5,
            frame: false,
            title: Lmkp.ts.msg('stakeholders-table_view'),
            xtype: 'lo_publicstakeholdertablepanel'
        }],
        layout: {
            align: 'stretch',
            type: 'vbox'
        },
        xtype: 'container'
    },{
        flex: 0.5,
        xtype: 'lo_publicmappanel'
    }]

});