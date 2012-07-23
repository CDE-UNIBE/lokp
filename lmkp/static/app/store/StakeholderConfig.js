Ext.define('Lmkp.store.StakeholderConfig', {
    extend: 'Ext.data.Store',
    requires: 'Lmkp.model.Config',
    model: 'Lmkp.model.Config',

    proxy: {
        type: 'ajax',
        url: '/config/form/stakeholders',
        reader: {
            type: 'json',
            root: undefined
        }
    }
});
