Ext.define('Lmkp.model.TagGroup', {
	extend: 'Ext.data.Model',
	
	fields: [{
		type: 'int',
		name: 'id'
	}],
	
	associations: [{
		type: 'hasMany',
		model: 'Lmkp.model.Tag',
		name: 'tags'
	}, {
		type: 'belongsTo',
		model: 'Lmkp.model.Activity',
		name: 'activity',
                getterName: 'getActivity'
	}, {
		type: 'hasMany', // this should be 1-to-1 (belongsTo), but does not seem to work.
		model: 'Lmkp.model.MainTag',
		name: 'main_tag'
	}]
});