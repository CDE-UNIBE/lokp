Ext.define('Lmkp.view.moderation.Main', {
    extend: 'Ext.tab.Panel',
    alias: 'widget.lo_moderationpanel',

    requires: [
        'Lmkp.view.moderation.OverviewTab',
        'Lmkp.view.moderation.PendingTab'
    ],

    frame: false,
    border: 0,
    defaults: {
        border: 0,
        frame: false,
        bodyPadding: 5
    },
    items: [
        {
            xtype: 'lo_moderationoverviewtab'
        }, {
            xtype: 'lo_moderationpendingtab',
            itemId: 'pendingtab'
        }
    ]

});