Ext.define('Lmkp.store.Config', {
    extend: 'Ext.data.Store',
    requires: 'Lmkp.model.Config',
    model: 'Lmkp.model.Config',
    
    proxy: {
        type: 'ajax',
        url: '/config/form',
        reader: {
            type: 'json',
            root: undefined
        }
    }
});
