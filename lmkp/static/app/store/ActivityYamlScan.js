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

    proxy: {
        type: 'ajax',
        url: '/config/scan/activities',
        reader: {
                type: 'json'
        },
        folderSort: true
    }

});
