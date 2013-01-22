/**
 *
 */
Ext.define('Lmkp.store.CompareMetadata', {
    extend: 'Ext.data.Store',

    autoLoad: false,
    fields: [
        'ref_version',
        'ref_timestamp',
        'new_version',
        'new_timestamp',
        'identifier',
        'type',
        'recalculated'
    ],

    proxy: {
        type: 'ajax',
        reader: {
            type: 'json',
            root: 'metadata'
        }
    }
});