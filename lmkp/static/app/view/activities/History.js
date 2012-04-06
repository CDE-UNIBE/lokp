Ext.define('Lmkp.view.activities.History', {
	extend: 'Ext.panel.Panel',
	alias: ['widget.activityHistoryTab'],
	
	id: 'activityHistoryTab',
	
	bodyPadding: 5,
	// html: 'Select an activity above to show its history',
	
	layout: {
        type:'vbox',
        padding:'5',
        align:'stretch'
    },
    defaults: {
    	margins:'0 0 5 0',
    	bodyPadding: 5,
    },
    
    // initial item
    items: [{
    	xtype: 'panel',
    	border: 0,
    	name: 'history_initial',
    	html: 'Select an activity above to show its history',
    	collapsible: false,
    	collapsed: false
    }]
	
});
