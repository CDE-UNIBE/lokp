Ext.define('Lmkp.view.activities.Details', {
	extend: 'Ext.panel.Panel',
	alias: ['widget.activityDetailTab'],
	
	id: 'activityDetailTab',
	
	bodyPadding: 5,
	
	layout: {
        type:'vbox',
        align:'stretch'
    },
    defaults: {
    	margins:'0 0 5 0',
    	bodyPadding: 5
    },
	
	// initial item
    items: [{
    	xtype: 'panel',
    	border: 0,
    	name: 'details_initial',
    	html: 'Select an activity above to show its details',
    	collapsible: false,
    	collapsed: false
    }]
	
});
