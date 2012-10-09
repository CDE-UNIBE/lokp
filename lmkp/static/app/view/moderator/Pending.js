Ext.define('Lmkp.view.moderator.Pending' ,{
    extend: 'Ext.container.Container',
    alias : ['widget.lo_moderatorpendingpanel'],

    requires: [
    'Lmkp.store.PendingActivityGrid',
    'Lmkp.store.PendingStakeholderGrid',
    'Lmkp.view.moderator.Review'
    ],

    layout: {
        type: 'hbox',
        align: 'stretch'
    },

    border: false,

    frame: false,

    items: [{
        flex: 0.5,
        layout: {
            type: 'vbox',
            align: 'stretch'
        },
        items: [{
            xtype: 'gridpanel',
            flex: 0.5,
            split: true,
            title: Lmkp.ts.msg("activities_title"),
            itemId: 'activityGrid',
            store: 'PendingActivityGrid',
            viewConfig: {
                stripeRows: false
            },
            // grid columns
            columns: [{
                header: 'Complete',
                name: 'completeColumn',
                dataIndex: 'missing_keys',
                flex: 0,
                sortable: true
            }, {
                header: Lmkp.ts.msg('date-label'),
                name: 'datecolumn',
                dataIndex: 'timestamp',
                flex: 0,
                sortable: true
            }, {
                header: Lmkp.ts.msg('activity_db-key-country'),
                name: 'activityCountryColumn',
                dataIndex: Lmkp.ts.msg('activity_db-key-country'),
                flex: 1,
                sortable: true
            }, {
                header: Lmkp.ts.msg('activity_db-key-yearofagreement'),
                name: 'yearofinvestmentcolumn',
                dataIndex: Lmkp.ts.msg('activity_db-key-yearofagreement'),
                flex: 0,
                sortable: true
            }],
            dockedItems: [{
                xtype: 'pagingtoolbar',
                id: 'pendingActivityGridPagingToolbar',
                store: 'PendingActivityGrid',
                dock: 'bottom',
                enableOverflow: false,
                displayInfo: true,
                beforePageText: Lmkp.ts.msg('gui_paging-before'),
                afterPageText: Lmkp.ts.msg('gui_paging-after'),
                displayMsg: Lmkp.ts.msg('activities_paging-message'),
                emptyMsg: '<b>' + Lmkp.ts.msg('activities_paging-empty') + '</b>'
            }]
        }, {
            xtype: 'gridpanel',
            flex: 0.5,
            split: true,
            title: Lmkp.ts.msg("stakeholders_title"),
            itemId: 'stakeholderGrid',
            store: 'PendingStakeholderGrid',
            viewConfig: {
                stripeRows: false
            },
            // grid columns
            columns: [
                {
                header: 'Complete',
                name: 'completeColumn',
                dataIndex: 'missing_keys',
                flex: 0,
                sortable: true
            }, {
                header: Lmkp.ts.msg('date-label'),
                name: 'datecolumn',
                dataIndex: 'timestamp',
                flex: 0,
                sortable: true
            }, {
                header: Lmkp.ts.msg('stakeholder_db-key-name'),
                name: 'stakeholdernamecolumn',
                dataIndex: Lmkp.ts.msg('stakeholder_db-key-name'),
                flex: 1,
                sortable: true
            }, {
                header: Lmkp.ts.msg('stakeholder_db-key-country'),
                name: 'stakeholdercountrycolumn',
                dataIndex: Lmkp.ts.msg('stakeholder_db-key-country'),
                flex: 0,
                sortable: true
            }
            ],
            dockedItems: [
            {
                xtype: 'pagingtoolbar',
                id: 'pendingStakeholderGridPagingToolbar',
                store: 'PendingStakeholderGrid',
                dock: 'bottom',
                enableOverflow: false,
                displayInfo: true,
                beforePageText: Lmkp.ts.msg('gui_paging-before'),
                afterPageText: Lmkp.ts.msg('gui_paging-after'),
                displayMsg: Lmkp.ts.msg('stakeholders_paging-message'),
                emptyMsg: '<b>' + Lmkp.ts.msg('stakeholders_paging-empty') + '</b>'
            }
            ]
        }],
        xtype: 'container'
    },{
        flex: 0.5,
        layout: {
            type: 'vbox',
            align: 'stretch'
        },
        xtype: 'lo_moderatorreviewpanel'
    }]

});