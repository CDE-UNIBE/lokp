Ext.define('Lmkp.model.Config', {
    extend: 'Ext.data.Model',
    fields: [
        'name',
        'fieldLabel',
        'xtype',
        'allowBlank',
        'store'
    ],
    proxy: {
        type: 'ajax',
        url: '/config',
        extraParams: {
            format: 'ext'
        },
        reader: {
            type: 'json',
            root: undefined
        }
    }
});
