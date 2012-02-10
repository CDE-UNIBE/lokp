Ext.define('Lmkp.store.ActivityTree',{
    extend: 'Ext.data.TreeStore',

    autoLoad: true,

    /* data: {
        users: [
        {
            id: 1,
            uuid: 83383829
        },{
            id: 2,
            uuid: 9392332
        }]
    },
     */

    proxy: {
        type: 'ajax',
        url: '/static/getdata.json',
        reader: {
            type: 'json',
            root: 'activities'
        }
    },

    listeners: {
        beforeload: {
            fn: function (store, users){
                console.log('Lmkp.store.ActivityTreeStore: beforeload');
            }
        }
    },

    requires: 'Lmkp.model.Activity',
    model: 'Lmkp.model.Activity',

    fields: ['id', 'uuid']

})