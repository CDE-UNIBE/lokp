Ext.define('Lmkp.model.YamlScan', {
	extend: 'Ext.data.Model',
	
	fields: [{
		name: 'value',
		type: 'string'
	}, {
		name: 'translation',
		type: 'string'
	}, {
		name: 'exists',
		type: 'boolean'
	}, {
		name: 'mandatory',
		type: 'boolean'
	}],
	
	proxy: {
		type: 'ajax',
		url: '/config/scan',
		reader: {
			type: 'json'
		},
		folderSort: true
	}
});
