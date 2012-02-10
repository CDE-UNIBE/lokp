Ext.define('Lmkp.view.manage.activities.TreePanel',{
    extend: 'Ext.tree.Panel',

    alias: [ 'widget.manageactivitiestreepanel' ],

    rootVisible: false,
    store: {
        proxy: {
            type: 'ajax',
            url: '/activities/tree',
            reader: {
                type: 'json'
            }
        }
    }
    
});