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

    title: Lmkp.ts.msg('gui_show-pending-versions'),
    
    items: [
        {
            title: Lmkp.ts.msg('activities_pending-versions'),
            xtype: 'gridpanel',
            itemId: 'pendingActivityGridPanel',
            store: 'PendingActivityGrid',
            columns: [
                {
                    header: Lmkp.ts.msg('gui_id'),
                    dataIndex: 'id',
                    flex: 1,
                    name: 'identifierColumn'
                }, {
                    header: Lmkp.ts.msg('gui_last-change'),
                    dataIndex: 'timestamp'
                }, {
                    header: Lmkp.ts.msg('gui_versions-pending'),
                    dataIndex: 'pending_count'
                }, {
                    xtype: 'templatecolumn',
                    name: 'compareButtonColumn',
                    flex: 0,
                    width: 24,
                    tpl: '<img src="/static/img/magnifier.png" style="cursor:pointer;" title="' + Lmkp.ts.msg('gui_show-details') + '">'
                }
            ]
        }, {
            xtype: 'pagingtoolbar',
            id: 'pendingActivitiesGridPagingToolbar',
            store: 'PendingActivityGrid',
            dock: 'bottom',
            flex: 0,
            enableOverflow: false,
            displayInfo: true,
            beforePageText: Lmkp.ts.msg('gui_paging-before'),
            afterPageText: Lmkp.ts.msg('gui_paging-after'),
            displayMsg: Lmkp.ts.msg('activities_pending-paging-message'),
            emptyMsg: '<b>' + Lmkp.ts.msg('activities_pending-paging-empty') + '</b>'
        }, {
            title: Lmkp.ts.msg('stakeholders_pending-versions'),
            xtype: 'gridpanel',
            itemId: 'pendingStakeholderGridPanel',
            store: 'PendingStakeholderGrid',
            columns: [
                {
                    header: Lmkp.ts.msg('gui_id'),
                    dataIndex: 'id',
                    flex: 1,
                    name: 'identifierColumn'
                }, {
                    header: Lmkp.ts.msg('gui_last-change'),
                    dataIndex: 'timestamp'
                }, {
                    header: Lmkp.ts.msg('gui_versions-pending'),
                    dataIndex: 'pending_count'
                }, {
                    xtype: 'templatecolumn',
                    name: 'compareButtonColumn',
                    flex: 0,
                    width: 24,
                    tpl: '<img src="/static/img/magnifier.png" style="cursor:pointer;" title="' + Lmkp.ts.msg('gui_show-details') + '">'
                }
            ]
         }, {
            xtype: 'pagingtoolbar',
            id: 'pendingStakeholdersGridPagingToolbar',
            store: 'PendingStakeholderGrid',
            dock: 'bottom',
            flex: 0,
            enableOverflow: false,
            displayInfo: true,
            beforePageText: Lmkp.ts.msg('gui_paging-before'),
            afterPageText: Lmkp.ts.msg('gui_paging-after'),
            displayMsg: Lmkp.ts.msg('stakeholders_pending-paging-message'),
            emptyMsg: '<b>' + Lmkp.ts.msg('stakeholders_pending-paging-empty') + '</b>'
        }
    ]
});


