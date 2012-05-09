Ext.define('Lmkp.model.TagGroup', {
	extend: 'Ext.data.Model',
	
	fields: [{
		type: 'string',
		name: 'id'
	}, {
		type: 'string',
		name: 'main_key'
	}],
	
	belongsTo: 'Lmkp.model.Activity',
	hasMany: [{
		model: 'Lmkp.model.Tag',
		name: 'tags'
	}]
});