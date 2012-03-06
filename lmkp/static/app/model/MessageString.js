Ext.define('Lmkp.model.MessageString',{
    extend: 'Ext.data.Model',

    fields: [{
        name: 'msgid',
        type: 'string'
    },{
        name: 'msgstr',
        type: 'string'
    }],
    idProperty: 'msgid',
    proxy: {
        type: 'ajax',
        url: '/lang'
    }
});