/**
 *
 */
Ext.define('Lmkp.store.CompareMetadata', {
    extend: 'Ext.data.Store',

    autoLoad: false,
    fields: [
        'ref_version',
        'ref_timestamp',
        'ref_userid',
        'ref_username',
        'new_version',
        'new_timestamp',
        'new_userid',
        'new_username',
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