Ext.define('Lmkp.view.moderator.Pending' ,{
    extend: 'Ext.panel.Panel',
    alias : ['widget.lo_moderatorpendingpanel'],

    requires: [
    'Lmkp.store.PendingActivityGrid'
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
            flex: 1,
            border: false,
            split: true,
            itemId: 'resultgrid',
            store: 'PendingActivityGrid',
            viewConfig: {
                stripeRows: false
            },
            // grid columns
            columns: [{
                header: Lmkp.ts.msg("activity-nameofinvestor"),
                name: 'nameofinvestorcolumn',
                dataIndex: Lmkp.ts.msg("activity-nameofinvestor"),
                flex: 1,
                sortable: true
            }, {
                header: Lmkp.ts.msg('activity-yearofinvestment'),
                name: 'yearofinvestmentcolumn',
                dataIndex: Lmkp.ts.msg('activity-yearofinvestment'),
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
        }],
        xtype: 'panel'
    },{
        flex: 0.5,
        html: 'this <i>will</i> be the future comparison panel',
        xtype: 'panel'
    }]

});