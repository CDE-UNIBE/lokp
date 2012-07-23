Ext.define('Lmkp.view.editor.ActivityTable',{
    extend: 'Ext.panel.Panel',
    alias: ['widget.lo_editoractivitytablepanel'],

    requires: [
    'Lmkp.view.activities.Filter'
    ],

    layout: {
        type: 'vbox',
        align: 'stretch'
    },
    border: 0,
    frame: false,

    items: [
        {
            xtype: 'lo_editoractivityfilterpanel'
        },{
            xtype: 'gridpanel',
            flex: 0.5,
            border: false,
            split: true,
            itemId: 'activityGrid',
            store: 'ActivityGrid',
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
                xtype: 'toolbar',
                dock: 'top',
                items: [{
                    boxLabel: Lmkp.ts.msg('filter-apply_spatial'),
                    checked: true,
                    itemId: 'spatialFilterCheckbox',
                    xtype: 'checkbox'
                }, {
                    xtype: 'checkbox',
                    boxLabel: Lmkp.ts.msg('filter-connect_to_stakeholders'),
                    itemId: 'filterConnectAtoSH'
                }]
            },{
                xtype: 'pagingtoolbar',
                id: 'activityGridPagingToolbar',
                store: 'ActivityGrid',
                dock: 'bottom',
                enableOverflow: false,
                displayInfo: true,
                beforePageText: Lmkp.ts.msg("activitypaging-before"),
                afterPageText: Lmkp.ts.msg("activitypaging-after"),
                displayMsg: Lmkp.ts.msg("activitypaging-message"),
                emptyMsg: '<b>' + Lmkp.ts.msg("activitypaging-empty") + '</b>'
            }
        ]
    }],

    /**
     * Returns the spatial filter checkbox
     */
    getSpatialFilterCheckbox: function(){
        return Ext.ComponentQuery.query('checkbox[itemId="spatialFilterCheckbox"]')[0];
    }

});