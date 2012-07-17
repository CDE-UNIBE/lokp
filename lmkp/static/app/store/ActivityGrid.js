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
        // Add the bounding box for the whole world as initial extra parameter
        // for the bounding box.
        // The bounding box is specified in the spherical mercator projection.
        extraParams: {
            bbox: "-20037508.34,-20037508.34,20037508.34,20037508.34",
            epsg: 900913
        },
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