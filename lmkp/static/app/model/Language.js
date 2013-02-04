Ext.define('Lmkp.model.Language', {
	extend: 'Ext.data.Model',
	
	fields: [{
		name: 'locale',
		type: 'string'
	}, {
		name: 'english_name',
		type: 'string'
	}, {
		name: 'local_name',
		type: 'string'
	}]

});
