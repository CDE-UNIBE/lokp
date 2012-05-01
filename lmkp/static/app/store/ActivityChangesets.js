Ext.define('Lmkp.store.ActivityChangesets', {
	extend: 'Ext.data.Store',
	
	requires: 'Lmkp.model.ActivityChangeset',
	model: 'Lmkp.model.ActivityChangeset',
	
	pageSize: 10,
	// remoteSort: true,
	
	proxy: {
		type: 'ajax',
		url: '/changesets',
		reader: {
			type: 'json',
			root: 'activities',
			totalProperty: 'activities_count'
		},
		startParam: 'offset'
	}
});
