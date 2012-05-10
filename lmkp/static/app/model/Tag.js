Ext.define('Lmkp.model.Tag', {
	extend: 'Ext.data.Model',
	
	fields: [{
		type: 'string',
		name: 'key'
	}, {
		type: 'string',
		name: 'value'
	}, {
		type: 'string',
		name: 'id'
	}],
	
	belongsTo: 'Lmkp.model.TagGroup'
});