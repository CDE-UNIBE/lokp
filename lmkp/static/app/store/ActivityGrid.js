Ext.define('Lmkp.store.ActivityGrid', {
    extend: 'Ext.data.Store',
    requires: 'Lmkp.model.ActivityGrid',
    model: 'Lmkp.model.ActivityGrid',
    
    pageSize: 10,
    autoLoad: true,
    remoteSort: true,
    
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