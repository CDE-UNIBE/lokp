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
            title: 'Overview',
                xtype: 'lo_moderationoverviewtab'
        }, {
            title: 'Show Pending',
            xtype: 'lo_moderationpendingtab'
        }
    ]

});