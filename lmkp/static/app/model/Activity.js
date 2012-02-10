Ext.define('Lmkp.model.Activity', {
    extend: 'Ext.data.Model',

    fields: [
    {
        name: 'id',
        type: 'int'
    },

    {
        name: 'uuid',
        type: 'int'
    }
    ],

    proxy: {
        type: 'ajax',
        url: '/static/getdata.json',
        reader: {
            type: 'json',
            root: 'activities'
        }
    }
});