Ext.define('Lmkp.view.DetailPanel', {
	extend: 'Ext.panel.Panel',
	alias: ['widget.detailPanel'],
	
	buttons: Lmkp.toolbar,
	id: 'detailPanel', // ??
	
	bodyPadding: 5,
	html: 'Select an activity above to show its details.',
	
	initComponent: function() {
		this.callParent(arguments);
	}
});
