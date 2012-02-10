Ext.define('Lmkp.model.Activity', {
    extend: 'Ext.data.Model',

    fields: [{
        name: 'id',
        type: 'int'
    },{
        name: 'year_of_investment',
        type: 'int'
    },{
        name: 'area',
        type: 'float'
    },{
        name: 'status',
        type: 'string'
    },{
        name: 'Spatial uncertainty',
        type: 'string'
    }],

    proxy: {
        type: 'ajax',
        url: '/activities/read',
        reader: {
            type: 'json',
            root: 'activities'
        }
    }
});