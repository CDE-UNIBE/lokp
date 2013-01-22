Ext.define('Lmkp.view.moderation.PendingTab', {
    extend: 'Ext.container.Container',
    alias: 'widget.lo_moderationpendingtab',

    requires: [
        'Lmkp.store.PendingActivityGrid',
        'Lmkp.store.PendingStakeholderGrid'
    ],

    layout: {
        type: 'vbox',
        align: 'stretch'
    },
    bodyPadding: 0,
    
    defaults: {
        flex: 0.5,
        border: 0
    },
    
    items: [
        {
            title: 'Pending Activities',
            xtype: 'gridpanel',
            itemId: 'pendingActivityGridPanel',
            store: 'PendingActivityGrid',
            columns: [
                {
                    header: 'ID',
                    dataIndex: 'id',
                    flex: 1
                }, {
                    header: 'Latest edit',
                    dataIndex: 'timestamp'
                }, {
                    header: 'Versions pending',
                    dataIndex: 'pending_count'
                }, {
                    xtype: 'templatecolumn',
                    name: 'compareButtonColumn',
                    tpl: '[C]'
                }
            ]
        }, {
            title: 'Pending Stakeholders',
            xtype: 'gridpanel',
            itemId: 'pendingStakeholderGridPanel',
            store: 'PendingStakeholderGrid',
            columns: [
                {
                    header: 'ID',
                    dataIndex: 'id',
                    flex: 1
                }, {
                    header: 'Latest edit',
                    dataIndex: 'timestamp'
                }, {
                    header: 'Versions pending',
                    dataIndex: 'pending_count'
                }, {
                    xtype: 'templatecolumn',
                    name: 'compareButtonColumn',
                    tpl: '[C]'
                }
            ]
        }
    ]
});


