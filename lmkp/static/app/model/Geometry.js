Ext.define('Lmkp.model.Geometry', {
    extend: 'Ext.data.Model',

    fields: [{
        name: 'type',
        type: 'string'
    },{
        name: 'coordinates',
        type: Ext.Array
    }]
});