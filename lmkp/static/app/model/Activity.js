Ext.define('Lmkp.model.Activity', {
    extend: 'Ext.data.Model',

    fields: [{
        name: 'id',
        type: 'string'
    },{
        name: 'geometry',
        type: 'Lmkp.model.Point'
    }],
	
    hasMany: [{
        model: 'Lmkp.model.TagGroup',
        name: 'taggroups'
    }]
});
