Ext.define('Lmkp.store.StakeholderYamlScan', {
    extend: 'Ext.data.TreeStore',
    requires: 'Lmkp.model.ShYamlScan',
    model: 'Lmkp.model.ShYamlScan',

    remoteSort: false,
    sortOnLoad: true,
    sorters: {
        property: 'value',
        direction: 'ASC'
    }
});