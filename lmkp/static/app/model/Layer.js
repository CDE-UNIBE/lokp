Ext.define('Lmkp.model.Layer', {
    extend: 'Ext.data.Model',
    fields: [
        'id',
        'name'
    ]
    // proxy: {
        // type: 'ajax',
        // url: 'data/layers.json',
        // reader: {
            // type: 'json',
            // root: 'results'
        // }
    // }
});
