Ext.define('Lmkp.view.manage.activities.TreePanel',{
    extend: 'Ext.tree.Panel',

    alias: [ 'widget.manageactivitiestreepanel' ],

    rootVisible: true,

    layout: 'fit',

    store: {
        autoLoad: true,
        model: 'Lmkp.model.ActivityTree'
    },

    root: {
        id: 'root',
        text: 'Root',
        expanded: true
    },

    /*store: {
        model: 'Lmkp.model.ActivityList',
        autoLoad: true
    },*/

    columns: [{
        //id: 'id-column',
        xtype: 'treecolumn',
        dataIndex: 'name',
        //text: 'Activity',
        flex: 2,
        text: 'Name'
    }]
    
});