Ext.define('Lmkp.view.manage.activities.TreePanel',{
    extend: 'Ext.tree.Panel',

    alias: [ 'widget.manageactivitiestreepanel' ],

    html: 'Zis is ze zreepanel',

    store: Ext.create('Ext.data.TreeStore', {
        root: {
            expanded: true,
            children: [
                { text: "detention", leaf: true },
                { text: "homework", expanded: true, children: [
                        { text: "book report", leaf: true },
                        { text: "alegrbra", leaf: true}
                    ] },
                { text: "buy lottery tickets", leaf: true }
            ]
        }
    }),
    rootVisible: false,

    initComponent: function(){
        this.callParent(arguments);
    }
});