Ext.define('Lmkp.model.Activity', {
    extend: 'Ext.data.Model',

    idProperty: '_id',

    fields: [{
        name: 'id', // activity_identifier (UID)
        type: 'string'
    }, {
        name: 'version',
        type: 'int'
    }, {
        name: 'status',
        type: 'string'
    }, {
        name: 'timestamp',
        type: 'string'
    }, {
        name: 'geometry',
        type: 'Lmkp.model.Point'
    }, {
        name: 'missing_keys',
        type: 'array'
    }],
	
    hasMany: [{
        model: 'Lmkp.model.TagGroup',
        name: 'taggroups'
    }, {
        model: 'Lmkp.model.Involvement',
        name: 'involvements'
    }],

    isEmpty: function() {
        var empty = true;
        var taggroupStore = this.taggroups();
        taggroupStore.each(function(taggroup) {
            if (empty && taggroup.get('id') != 0) {
                empty = empty && false;
            } else {
                empty = empty && true;
            }
        });
        return empty;
    }
});
