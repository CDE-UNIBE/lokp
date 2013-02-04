Ext.define('Lmkp.store.ActivityVector', {
    extend: 'GeoExt.data.FeatureStore',

    extraParams: {
        bbox: "-20037508.34,-20037508.34,20037508.34,20037508.34",
        epsg: 900913,
        // Do not load involvements in grid for faster loading
        involvements: 'none'
    },

    fields: [{
        name: "status",
        type: "string"
    },{
        name: "version",
        type: "int"
    },{
        name: "activity_identifier",
        type: "string"
    }],

    // A workaround to disable the paging
    pageSize: 500

});