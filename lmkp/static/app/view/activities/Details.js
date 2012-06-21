Ext.define('Lmkp.view.activities.Details', {
	extend: 'Ext.panel.Panel',
	alias: ['widget.activityDetailTab'],
	
	id: 'activityDetailTab',

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
    }]
	
});
