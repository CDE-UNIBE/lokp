Ext.define('Lmkp.view.translation.Main', {
    extend: 'Ext.tab.Panel',
    alias: 'widget.lo_translationpanel',

    frame: false,
    border: 0,
    defaults: {
        border: 0,
        frame: false,
        bodyPadding: 5
    },
    items: [
        {
            xtype: 'lo_translationoverviewtab'
        }, {
            xtype: 'lo_translationkeyvaluetree',
            itemId: 'keyvalueactivities',
            title: 'Activities'
//            postUrl: '/config/add/activities',
//            store: null
//            html: 'asdf'
        }
    ]
});