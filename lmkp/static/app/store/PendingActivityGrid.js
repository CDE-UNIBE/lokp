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

    // initial sorting
    sortOnLoad: true,
    sorters: {
        property: 'timestamp',
        direction : 'DESC'
    },

    proxy: {
        type: 'ajax',
        url: '/activities',
        extraParams: {
            status: 'pending',
            bounds: 'user',
            mark_complete: 'true'
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