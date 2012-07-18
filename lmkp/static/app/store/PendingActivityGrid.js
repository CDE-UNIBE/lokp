Ext.define('Lmkp.store.PendingActivityGrid', {
    extend: 'Ext.data.Store',

    // all are needed to build relation
    requires: [
        'Lmkp.model.Activity',
        'Lmkp.model.TagGroup',
        'Lmkp.model.Tag',
        'Lmkp.model.MainTag',
        'Lmkp.model.Point',
        'Lmkp.model.Involvement'
    ],

    model: 'Lmkp.model.Activity',

    pageSize: 10,
    remoteSort: true,

    proxy: {
        type: 'ajax',
        url: '/activities',
        extraParams: {
            status: 'pending',
            bounds: 'profile'
        },
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