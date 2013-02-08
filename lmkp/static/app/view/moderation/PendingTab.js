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
                    flex: 1,
                    name: 'identifierColumn'
                }, {
                    header: 'Latest edit',
                    dataIndex: 'timestamp'
                }, {
                    header: 'Versions pending',
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
            displayMsg: 'Displaying pending Activities {0} - {1} of {2}', // TODO
            emptyMsg: '<b>' + 'No pending Activities to display' + '</b>' // TODO
        }, {
            title: 'Pending Stakeholders',
            xtype: 'gridpanel',
            itemId: 'pendingStakeholderGridPanel',
            store: 'PendingStakeholderGrid',
            columns: [
                {
                    header: 'ID',
                    dataIndex: 'id',
                    flex: 1,
                    name: 'identifierColumn'
                }, {
                    header: 'Latest edit',
                    dataIndex: 'timestamp'
                }, {
                    header: 'Versions pending',
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
            displayMsg: 'Displaying pending Stakeholders {0} - {1} of {2}', // TODO
            emptyMsg: '<b>' + 'No pending Stakeholders to display' + '</b>' // TODO
        }
    ]
});


