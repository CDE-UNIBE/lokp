Ext.define('Lmkp.view.DetailPanel', {
	extend: 'Ext.tab.Panel',
	alias: ['widget.detailPanel'],
	
	id: 'detailPanel',
	
	dockedItems: Lmkp.toolbar,
	
	activeTab: 0,
	
	items: [{
		title: 'Details',
		xtype: 'activityDetailTab'
	}, {
		title: 'History',
		xtype: 'activityHistoryTab'
	}],
	
	initComponent: function() {
		this.callParent(arguments);
	}
});
