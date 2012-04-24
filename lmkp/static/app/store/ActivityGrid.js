Ext.define('Lmkp.store.ActivityGrid', {
    extend: 'Ext.data.Store',
    requires: ['Lmkp.model.Activity','Lmkp.model.TagGroup'], // both are needed to build relation
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