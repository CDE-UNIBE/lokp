Ext.define('Lmkp.model.Activity', {
    extend: 'Ext.data.Model',

    fields: [{
        name: 'id', // activity_identifier (UID)
        type: 'string'
    }, {
        name: 'version',
        type: 'int'
    }, {
        name: 'geometry',
        type: 'Lmkp.model.Point'
    }],
	
    hasMany: [{
        model: 'Lmkp.model.TagGroup',
        name: 'taggroups'
    }, {
        model: 'Lmkp.model.Involvement',
        name: 'involvements'
    }]
});
