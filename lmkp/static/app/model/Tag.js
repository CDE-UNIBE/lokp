Ext.define('Lmkp.model.Tag', {
	extend: 'Ext.data.Model',
	
	fields: [{
		type: 'string',
		name: 'key'
	}, {
		type: 'string',
		name: 'value'
	}],
	
	belongsTo: 'Lmkp.model.TagGroup'
});