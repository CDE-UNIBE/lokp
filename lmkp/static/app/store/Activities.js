Ext.define('Lmkp.store.Activities',{
    extend: 'Ext.data.Store',

    autoLoad: false,

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