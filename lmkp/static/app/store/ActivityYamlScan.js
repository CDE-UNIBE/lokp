Ext.define('Lmkp.store.ActivityYamlScan', {
    extend: 'Ext.data.TreeStore',
    requires: 'Lmkp.model.YamlScan',
    model: 'Lmkp.model.YamlScan',

    remoteSort: false,
    autoLoad: true,
    sortOnLoad: true,
    sorters: {
        property: 'value',
        direction: 'ASC'
    },

    // TODO: Also check the model
    proxy: {
        type: 'ajax',
        url: '/config/scan/activities',
        reader: {
                type: 'json'
        },
        folderSort: true
    }

});
