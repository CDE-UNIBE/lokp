Ext.define('Lmkp.model.ActivityTest', {
    extend: 'Ext.data.Model',

    autoLoad: true,

    requires: [
        'Lmkp.reader.GeoJson'
    ],

    fields:[{
        name: 'id',
        type: 'int'
    },{
        name: 'name',
        type: 'string'
    }],

    proxy: {
        type: 'ajax',
        url: '/geojson',
        reader: 'json'
            
    /*{
            type: 'geojson'
        }*/
    },

    constructor: function(config){
        return this.callParent(config)
    }

});