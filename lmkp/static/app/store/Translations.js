Ext.define('Lmkp.store.Translations',{
    extend: 'Ext.data.Store',

    autoLoad: true,

    model: 'Lmkp.model.MessageString',

    proxy: {
        type: 'ajax',
        url: '/lang'
    },

    storeId: 'translations',

    getById2: function(id){
        console.log(id);
        console.log(this.find('msgid', new RegExp("/" + id + "/")));
        return this.getAt(this.find('msgid', id));
    }
});