Ext.define('Lmkp.model.ActivityGrid', {
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
        url: '/activities/json',
        reader: {
            root: 'data',
            type: 'json',
            totalProperty: 'total'
        }
    }

});