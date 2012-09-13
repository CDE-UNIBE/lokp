Ext.define('Lmkp.model.Point', {
    extend: 'Ext.data.Model',

    fields: [{
        name: 'type',
        type: 'string'
    },{
        name: 'coordinates',
        type: Ext.Array
    }]
});