Ext.define('Lmkp.view.manage.activities.TreePanel',{
    extend: 'Ext.tree.Panel',

    alias: [ 'widget.manageactivitiestreepanel' ],

    rootVisible: false,

    layout: 'fit',

    store: {
        autoLoad: true,
        model: 'Lmkp.model.ActivityTree',
        proxy: {
            type: 'ajax',
            url: '/activities/tree',
            extraParams: {
                status: 'pending,active'
            },
            reader: {
                root: 'children',
                type: 'json'
            }
        }
    },

    /*store: {
        model: 'Lmkp.model.ActivityList',
        autoLoad: true
    },*/

    columns: [{
        //id: 'id-column',
        xtype: 'treecolumn',
        dataIndex: 'Name',
        //text: 'Activity',
        flex: 2,
        text: 'Name'
    }]
    
});