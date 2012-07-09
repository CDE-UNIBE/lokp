Ext.define('Lmkp.store.ActivityGrid', {
    extend: 'Ext.data.Store',
    
    // all are needed to build relation
    requires: [
    'Lmkp.model.Activity',
    'Lmkp.model.TagGroup',
    'Lmkp.model.Tag',
    'Lmkp.model.MainTag',
    'Lmkp.model.Point'
    ],
    
    model: 'Lmkp.model.Activity',

    pageSize: 10,
    remoteSort: true,

    proxy: {
        type: 'ajax',
        url: '/activities',
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