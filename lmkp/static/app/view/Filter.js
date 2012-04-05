Ext.define('Lmkp.view.Filter', {
    extend: 'Ext.panel.Panel',
    alias: ['widget.filterPanel'],

    title: Lmkp.ts.msg("activities-title"),
    frame: false,

    layout: {
        type: 'vbox',
        padding: 5,
        align: 'stretch'
    },

    tbar: [{
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
    },{
        id: 'deleteAllFilters',
        text: Lmkp.ts.msg("deleteallfilter-button"),
        tooltip: Lmkp.ts.msg("deleteallfilter-tooltip"),
        iconCls: 'toolbar-button-delete',
        enableToggle: false
    }],
   	
    initComponent: function() {
        this.items = [{
            // attribute selection
            xtype: 'panel',
            id: 'filterForm',
            flex: 0,
            collapsible: true,
            collapsed: true, // TODO: For some reason, layout is not working (buttons disappear on Adding filter) when collapsed at start.
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
        }, {
            // filter results
            xtype: 'panel',
            flex: 1,
            border: false,
            layout: {
                type: 'vbox',
                align: 'stretch'
            },
            items: [{
                xtype: 'gridpanel',
                id: 'filterResults',
                store: 'ActivityGrid',
                viewConfig: {
                    stripeRows: false
                },
                columns: [{
                    header: Lmkp.ts.msg("name-column"),
                    name: 'namecolumn',
                    dataIndex: 'Name',
                    flex: 1,
                    sortable: true
                }],
                dockedItems: [{
                    xtype: 'pagingtoolbar',
                    store: 'ActivityGrid',
                    dock: 'bottom',
                    enableOverflow: true,
                    displayInfo: true,
                    beforePageText: Lmkp.ts.msg("activitypaging-before"),
                    afterPageText: Lmkp.ts.msg("activitypaging-after"),
                    displayMsg: Lmkp.ts.msg("activitypaging-message"),
                    emptyMsg: '<b>' + Lmkp.ts.msg("activitypaging-empty") + '</b>'
                }]
            }, {
                xtype: 'detailPanel',
                flex: 1
            }]
        }];
        this.callParent(arguments);
    }
});
