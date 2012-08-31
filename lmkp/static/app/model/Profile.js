Ext.define('Lmkp.model.Profile', {
    extend: 'Ext.data.Model',
	
    fields: [{
        name: 'profile',
        type: 'string'
    }, {
        name: 'name',
        type: 'string'
    }, {
        name: 'geometry',
        type: 'Lmkp.model.Geometry'
    },{
        name: 'active',
        type: 'boolean',
        defaultValue: false
    }],

    idProperty: 'profile',
	
    proxy: {
        type: 'ajax',
        url: '/profiles/all',
        reader: {
            type: 'json',
            root: 'data'
        }
    }
});
