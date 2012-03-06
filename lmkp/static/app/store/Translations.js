Ext.define('Lmkp.store.Translations',{
    extend: 'Ext.data.Store',

    alias: ["store.translations"],

    autoLoad: true,

    model: 'Lmkp.model.MessageString',

    proxy: {
        type: 'ajax',
        url: '/lang'
    },

    storeId: 'translations',

    getById: function(id){
        console.log(this);
        console.log(id);
        var index = this.find("msgid", new RegExp(id));
        console.log(index);
        return this.getAt(index).get("msgstr");
    }
});