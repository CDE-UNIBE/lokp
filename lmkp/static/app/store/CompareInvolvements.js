/**
 *
 */
Ext.define('Lmkp.store.CompareInvolvements', {
    extend: 'Ext.data.Store',

    autoLoad: false,
    fields: ['ref', 'new'],

    proxy: {
        type: 'ajax',
        reader: {
            type: 'json',
            root: 'involvements'
        }
    }
});
