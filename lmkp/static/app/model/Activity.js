Ext.define('Lmkp.model.Activity', {
	extend: 'Ext.data.Model',
	
	fields: [{
		name: 'id',
		type: 'string'
	}],
	
	hasMany: [{
		model: 'Lmkp.model.TagGroup',
		name: 'taggroups',
	}]
});
