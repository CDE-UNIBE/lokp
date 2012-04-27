Ext.define('Lmkp.model.ActivityChangeset', {
	extend: 'Ext.data.Model',
	
	fields: [{
		// status
		name: 'status',
		type: 'string'
	}, {
		// source
		name: 'source',
		type: 'string'
	}, {
		// username
		name: 'user',
		type: 'string'
	}, {
		// activity_identifier
		name: 'activity',
		type: 'string'
	}],
	
	proxy: {
		type: 'ajax',
		url: '/changesets',
		reader: {
			type: 'json',
			root: 'activities'
		}
	}
});
