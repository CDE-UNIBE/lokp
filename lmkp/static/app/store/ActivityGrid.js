Ext.define('Lmkp.store.ActivityGrid', {
    extend: 'Ext.data.Store',
    requires: 'Lmkp.model.ActivityGrid',
    model: 'Lmkp.model.ActivityGrid',
    
    pageSize: 10,
    autoLoad: true,
    remoteSort: true
});