Ext.define('Lmkp.store.StakeholderYamlScan', {
    extend: 'Ext.data.TreeStore',
    requires: 'Lmkp.model.YamlScan',
    model: 'Lmkp.model.YamlScan',

    remoteSort: false,
    sortOnLoad: true,
    sorters: {
        property: 'value',
        direction: 'ASC'
    },

    proxy: {
        type: 'ajax',
        url: '/config/scan/stakeholders',
        reader: {
            type: 'json'
        },
        folderSort: true
    }
});