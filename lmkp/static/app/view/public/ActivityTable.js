Ext.define('Lmkp.view.public.ActivityTable',{
    extend: 'Ext.container.Container',
    alias: ['widget.lo_publicactivitytablepanel'],

    requires: [
    'Lmkp.view.activities.Filter',
    'Ext.grid.column.Template'
    ],

    layout: {
        type: 'vbox',
        align: 'stretch'
    },
    border: 0,
    frame: false,

    config: {
        filterCount: 0
    },

    items: [{
        xtype: 'gridpanel',
        title: Lmkp.ts.msg('activities_title'),
        flex: 0.5,
        border: false,
        split: true,
        itemId: 'activityGrid',
        store: 'ActivityGrid',
        viewConfig: {
            stripeRows: false
        },
        // grid columns
        columns: [
            {
                header: Lmkp.ts.msg('gui_id'),
                name: 'activityIdentifierColumn',
                dataIndex: 'id',
                flex: 0,
                sortable: false
            }, {
                header: Lmkp.ts.msg('gui_last-change'),
                name: 'activityLastChangeColumn',
                dataIndex: 'timestamp',
                flex: 0,
                sortable: false,
                hidden: true
            }, {
                header: Lmkp.ts.msg('activity_db-key-spatialaccuracy'),
                name: 'activitySpatialAccuracyColumn',
                dataIndex: Lmkp.ts.msg('activity_db-key-spatialaccuracy'),
                flex: 0,
                sortable: true,
                hidden: true,
                doSort: function(state) {
                    var store = this.up('tablepanel').store;
                    if (store) {
                        store.doCustomSort(
                            Lmkp.ts.msg('activity_db-key-spatialaccuracy-original'),
                            state
                        );
                    }
                }
            }, {
                header: Lmkp.ts.msg('activity_db-key-negotiationstatus'),
                name: 'activityNegotiationStatusColumn',
                dataIndex: Lmkp.ts.msg('activity_db-key-negotiationstatus'),
                flex: 0,
                sortable: true,
                doSort: function(state) {
                    var store = this.up('tablepanel').store;
                    if (store) {
                        store.doCustomSort(
                            Lmkp.ts.msg('activity_db-key-negotiationstatus-original'),
                            state
                        );
                    }
                }
            }, {
                header: Lmkp.ts.msg('activity_db-key-country'),
                name: 'activityCountryColumn',
                dataIndex: Lmkp.ts.msg('activity_db-key-country'),
                flex: 0,
                sortable: true,
                hidden: true,
                doSort: function(state) {
                    var store = this.up('tablepanel').store;
                    if (store) {
                        store.doCustomSort(
                            Lmkp.ts.msg('activity_db-key-country-original'),
                            state
                        );
                    }
                }
            }, {
                header: Lmkp.ts.msg('activity_db-key-intendedarea'),
                name: 'activityIntendedAreaColumn',
                dataIndex: Lmkp.ts.msg('activity_db-key-intendedarea'),
                flex: 0,
                sortable: true,
                doSort: function(state) {
                    var store = this.up('tablepanel').store;
                    if (store) {
                        store.doCustomSort(
                            Lmkp.ts.msg('activity_db-key-intendedarea-original'),
                            state
                        );
                    }
                }
            }, {
                header: Lmkp.ts.msg('activity_db-key-intentionofinvestment'),
                name: 'activityIntentionOfInvestmentColumn',
                dataIndex: Lmkp.ts.msg('activity_db-key-intentionofinvestment'),
                flex: 1,
                sortable: true,
                doSort: function(state) {
                    var store = this.up('tablepanel').store;
                    if (store) {
                        store.doCustomSort(
                            Lmkp.ts.msg('activity_db-key-intentionofinvestment-original'),
                            state
                        );
                    }
                }
            }, {
                header: Lmkp.ts.msg('activity_db-key-datasource'),
                name: 'activityDataSourceColumn',
                dataIndex: Lmkp.ts.msg('activity_db-key-datasource'),
                flex: 0,
                sortable: true,
                hidden: true,
                doSort: function(state) {
                    var store = this.up('tablepanel').store;
                    if (store) {
                        store.doCustomSort(
                            Lmkp.ts.msg('activity_db-key-datasource-original'),
                            state
                        );
                    }
                }
            }, {
                xtype: 'templatecolumn',
                flex: 0,
                hideable: false,
                name: 'showDetailsColumn',
                width: 24,
                align: 'center',
                tpl: '<img src="static/img/information.png" style="cursor:pointer;" title="' + Lmkp.ts.msg('gui_show-details') + '">'
            }
        ],
        dockedItems: [{
            xtype: 'toolbar',
            id: 'activityGridTopToolbar',
            dock: 'top',
            items: ['->', {
                text: Lmkp.ts.msg('gui_clear-selection'),
                itemId: 'activityResetSelectionButton'
            }, {                    	
                text: Lmkp.ts.msg('gui_delete-all-filters'),
                itemId: 'activityDeleteAllFiltersButton'
            }]
        }]
    },{
        xtype: 'pagingtoolbar',
        id: 'activityGridPagingToolbar',
        store: 'ActivityGrid',
        dock: 'bottom',
        enableOverflow: false,
        displayInfo: true,
        beforePageText: Lmkp.ts.msg('gui_paging-before'),
        afterPageText: Lmkp.ts.msg('gui_paging-after'),
        displayMsg: Lmkp.ts.msg('activities_paging-message'),
        emptyMsg: '<b>' + Lmkp.ts.msg('activities_paging-empty') + '</b>'
    }],

    /**
 * Returns the spatial filter checkbox
 */
    getSpatialFilterCheckbox: function(){
        return Ext.ComponentQuery.query('checkbox[itemId="spatialFilterCheckbox"]')[0];
    }

});