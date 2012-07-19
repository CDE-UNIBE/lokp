Ext.define('Lmkp.view.editor.Table',{
    extend: 'Ext.panel.Panel',
    alias: ['widget.lo_editortablepanel'],

    requires: [
    'Lmkp.view.Filter'
    ],

    layout: 'border',

    border: false,

    frame: false,

    items: [{
        layout: {
            type: 'vbox',
            align: 'stretch'
        },
        items: [{
            // attribute selection
            xtype: 'panel',
            id: 'filterForm',
            flex: 0.5,
            //collapsible: true,
            //collapsed: true, // TODO: For some reason, layout is not working (buttons disappear on Adding filter) when collapsed at start.
            title: Lmkp.ts.msg("filter-title"),
            layout: {
                type: 'anchor'
            },
            // height: 500,
            bodyPadding: 5,
            items: [{
                xtype: 'panel',
                layout: {
                    type: 'hbox',
                    flex: 'stretch'
                },
                anchor: '100%',
                border: 0,
                items: [{
                    xtype: 'combobox',
                    store: ['and', 'or'],
                    name: 'logicalOperator',
                    value: 'and',
                    editable: false,
                    hidden: true,
                    fieldLabel: 'Logical operator'
                }, {
                    xtype: 'panel', // empty panel for spacing
                    flex: 1,
                    border: 0
                }, {
                    xtype: 'button',
                    name: 'addAttributeFilter',
                    text: Lmkp.ts.msg("addattributefilter-button"),
                    tooltip: Lmkp.ts.msg("addattributefilter-tooltip"),
                    iconCls: 'toolbar-button-add',
                    margin: '0 5 0 0',
                    flex: 0
                }, {
                    xtype: 'button',
                    name: 'addTimeFilter',
                    text: Lmkp.ts.msg("addtimefilter-button"),
                    tooltip: Lmkp.ts.msg("addtimefilter-tooltip"),
                    iconCls: 'toolbar-button-add',
                    flex: 0
                }]
            }]
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
                dock: 'top',
                items: [{
                    boxLabel: 'Apply spatial filter',
                    checked: true,
                    itemId: 'spatialFilterCheckbox',
                    xtype: 'checkbox'
                }],
                xtype: 'toolbar'
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
            }]
        }],
        region: 'center',
        xtype: 'panel'
    }],

    /**
     * Returns the spatial filter checkbox
     */
    getSpatialFilterCheckbox: function(){
        return Ext.ComponentQuery.query('checkbox[itemId="spatialFilterCheckbox"]')[0];
    }

});