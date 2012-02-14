Ext.define('Lmkp.view.manage.activities.TreePanel',{
    extend: 'Ext.tree.Panel',

    alias: [ 'widget.manageactivitiestreepanel' ],

    rootVisible: false,

    store: {
        autoLoad: true,
        model: 'Lmkp.model.Activity'
    },

    columns: [{
        id: 'id-column',
        xtype: 'treecolumn',
        dataIndex: 'name',
        text: 'id',
        flex: 1
    }]
    
});