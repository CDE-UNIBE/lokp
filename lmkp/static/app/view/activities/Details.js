Ext.define('Lmkp.view.activities.Details', {
    extend: 'Ext.panel.Panel',
    alias: ['widget.activityDetailTab'],
	
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
        border: 0,
        name: 'details_initial',
        html: Lmkp.ts.msg('activity-select'),
        collapsible: false,
        collapsed: false
    }],

    tbar: {
        dock: 'top',
        xtype: 'toolbar',
        items: [{
            enableToggle: true,
            itemId: 'show-all-details',
            pressed: true,
            text: 'Show all details'
        },{
            itemId: 'add-taggroup-button',
            text: 'Add further information',
            tooltip: 'Submit further information to an existing activity'
        }]
    }
	
});
