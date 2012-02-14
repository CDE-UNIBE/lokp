Ext.define('Lmkp.model.Activity', {
    extend: 'Ext.data.Model',

    fields: [{
        name: 'id',
        type: 'int'
    },{
        name: 'name',
        type: 'string'
    },{
        name: 'year_of_investment',
        type: 'int'
    },{
        name: 'area',
        type: 'float'
    },{
        name: 'project_status',
        type: 'string'
    },{
        name: 'Spatial uncertainty',
        type: 'string'
    },{
        name: 'leaf',
        type: 'bool'
    },{
        name: 'project_use',
        type: 'string'
    }],

    idProperty: 'id',

    proxy: {
        type: 'ajax',
        url: '/activities/read',
        reader: {
            type: 'json',
            root: 'activities'
        }
    }
});