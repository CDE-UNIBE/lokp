Ext.define('Lmkp.store.ActivityYamlScan', {
    extend: 'Ext.data.TreeStore',
    requires: 'Lmkp.model.YamlScan',
    model: 'Lmkp.model.YamlScan',

    remoteSort: false,
    sortOnLoad: true,
    sorters: {
        property: 'value',
        direction: 'ASC'
    }

});
