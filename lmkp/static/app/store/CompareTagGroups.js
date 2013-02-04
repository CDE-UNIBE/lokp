/**
 *
 */
Ext.define('Lmkp.store.CompareTagGroups', {
    extend: 'Ext.data.Store',

    autoLoad: false,
    fields: ['ref', 'new'],

    proxy: {
        type: 'ajax',
        reader: {
            type: 'json',
            root: 'taggroups'
        }
    }
});
