Ext.define('Lmkp.store.ActivityVector', {
    extend: 'GeoExt.data.FeatureStore',

    fields: [{
        name: "status",
        type: "string"
    },{
        name: "version",
        type: "int"
    },{
        name: "activity_identifier",
        type: "string"
    }]
});