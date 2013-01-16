/**
 *
 */
Ext.define('Lmkp.store.CompareVersions', {
    extend: 'Ext.data.Store',

    autoLoad: false,
    fields: [
        'version',
        'status',
        {
            name: 'display',
            convert: function(value, record) {
                // TODO: improve performance
                var statusStore = Ext.create('Lmkp.store.Status');

                var statusName = statusStore.getAt(record.get('status')-1);
                if (statusName) {
                    return record.get('version') + ' (' +
                        statusName.get('display_name') + ')';
                } else {
                    return record.get('version') + ' (' +
                        Lmkp.ts.msg('unknown') + ')';
                }
            }
        }
    ],

    proxy: {
        type: 'ajax',
        reader: {
            type: 'json',
            root: 'versions'
        }
    }
});
