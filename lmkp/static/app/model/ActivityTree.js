Ext.define('Lmkp.model.ActivityTree', {
    extend: 'Ext.data.Model',

    fields:[{
        name: 'id',
        type: 'int'
    },{
        name: 'name',
        type: 'string'
    }],

    proxy: {
        type: 'ajax',
        url: '/activities/tree',
        reader: {
            root: 'activities',
            type: 'json'
        }
    }

});