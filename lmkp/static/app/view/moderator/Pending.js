Ext.define('Lmkp.view.moderator.Pending' ,{
    extend: 'Ext.panel.Panel',
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
            border: false,
            split: true,
            title: Lmkp.ts.msg("activities-title"),
            itemId: 'activityGrid',
            store: 'PendingActivityGrid',
            viewConfig: {
                stripeRows: false
            },
            // grid columns
            columns: [{
                header: Lmkp.ts.msg("activity-attr_country"),
                name: 'activityCountryColumn',
                dataIndex: Lmkp.ts.msg("activity-attr_country"),
                flex: 1,
                sortable: true
            }, {
                header: Lmkp.ts.msg('activity-attr_yearofinvestment'),
                name: 'yearofinvestmentcolumn',
                dataIndex: Lmkp.ts.msg('activity-attr_yearofinvestment'),
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
                beforePageText: Lmkp.ts.msg("activitypaging-before"),
                afterPageText: Lmkp.ts.msg("activitypaging-after"),
                displayMsg: Lmkp.ts.msg("activitypaging-message"),
                emptyMsg: '<b>' + Lmkp.ts.msg("activitypaging-empty") + '</b>'
            }]
        }, {
            xtype: 'gridpanel',
            flex: 0.5,
            border: false,
            split: true,
            title: Lmkp.ts.msg("stakeholders-title"),
            itemId: 'stakeholderGrid',
            store: 'PendingStakeholderGrid',
            viewConfig: {
                stripeRows: false
            },
            // grid columns
            columns: [
                {
                    header: 'Name',
                    name: 'stakeholdernamecolumn',
                    dataIndex: 'Name',
                    flex: 1,
                    sortable: true
                }, {
                    header: 'Country',
                    name: 'stakeholdercountrycolumn',
                    dataIndex: 'Country',
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
                    beforePageText: Lmkp.ts.msg("activitypaging-before"),
                    afterPageText: Lmkp.ts.msg("activitypaging-after"),
                    displayMsg: Lmkp.ts.msg("stakeholder-paging_message"),
                    emptyMsg: '<b>' + Lmkp.ts.msg("stakeholder-paging_empty") + '</b>'
                }
            ]
        }],
        xtype: 'panel'
    },{
        flex: 0.5,
        layout: {
            type: 'vbox',
            align: 'stretch'
        },
        xtype: 'lo_moderatorreviewpanel'
    }]

});