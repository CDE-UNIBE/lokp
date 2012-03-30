Ext.define('Lmkp.model.Profile', {
	extend: 'Ext.data.Model',
	
	fields: [{
		name: 'profile',
		type: 'string'
	}, {
		name: 'name',
		type: 'string'
	}],
	
	proxy: {
		type: 'ajax',
		url: '/profiles/all',
		reader: {
			type: 'json',
			root: 'data'
		}
	}
});
