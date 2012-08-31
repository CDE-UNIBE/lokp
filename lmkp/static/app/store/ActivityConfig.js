Ext.define('Lmkp.store.ActivityConfig', {
    extend: 'Ext.data.Store',
    requires: 'Lmkp.model.Config',
    model: 'Lmkp.model.Config',
    
    proxy: {
        type: 'ajax',
        url: '/config/form/activities',
        reader: {
            type: 'json',
            root: undefined
        }
    }
});
