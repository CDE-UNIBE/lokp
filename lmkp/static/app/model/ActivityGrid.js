Ext.define('Lmkp.model.ActivityGrid', {
    extend: 'Ext.data.Model',

    fields: [{
        name: 'id',
        type: 'int'
    }, {
        name: 'name',
        type: 'string'
    }],
    idProperty: 'id',

    proxy: {
        type: 'ajax',
        url: '/activities/json',
        reader: {
            root: 'data',
            type: 'json',
            totalProperty: 'total'
        },
        startParam: 'offset',
        simpleSortMode: true,
        sortParam: 'order_by'
    }

});