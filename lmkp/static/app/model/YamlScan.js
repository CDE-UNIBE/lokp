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
	}, {
		name: 'keyvalue',
		type: 'string'
	}, {
		name: 'local',
		type: 'boolean'
	}],
	
	proxy: {
		type: 'ajax',
		url: '/config/scan/activities',
		reader: {
			type: 'json'
		},
		folderSort: true
	}
});
