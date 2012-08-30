Ext.define('Lmkp.view.public.ActivityTable',{
    extend: 'Ext.container.Container',
    alias: ['widget.lo_publicactivitytablepanel'],

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
            xtype: 'gridpanel',
            title: 'Activities',
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
                items: [
                    {
                        text: 'Filter',
                        itemId: 'activityFilterButton'
                    }
                ]
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