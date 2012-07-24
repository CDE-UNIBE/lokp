Ext.define('Lmkp.view.activities.Details', {
    extend: 'Ext.panel.Panel',
    alias: ['widget.lo_activitydetailtab'],
	
    itemId: 'activityDetailTab',

    bodyPadding: 5,
	
    layout: {
        type: 'anchor'
    },
    defaults: {
        margin: '0 0 5 0',
        anchor: '100%'
    },
	
    // initial item
    items: [{
        xtype: 'panel',
        name: 'details_initial',
        html: Lmkp.ts.msg('activity-select'),
        border: 0
    }],

    tbar: {
        dock: 'top',
        xtype: 'toolbar',
        items: [{
            enableToggle: true,
            itemId: 'show-all-details',
            pressed: true,
            scale: 'medium',
            text: Lmkp.ts.msg('details-toggle_all')
        },{
            itemId: 'add-taggroup-button',
            scale: 'medium',
            text: 'Add further information',
            tooltip: Lmkp.ts.msg('activities-add_further_information')
        }]
    }
	
});
