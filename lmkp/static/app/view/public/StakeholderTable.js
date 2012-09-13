Ext.define('Lmkp.view.public.StakeholderTable', {
    extend: 'Ext.container.Container',
    alias: ['widget.lo_publicstakeholdertablepanel'],

    requires: [
    'Lmkp.view.stakeholders.Filter'
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

    items: [
    {
        xtype: 'gridpanel',
        title: 'Stakeholders',
        flex: 0.5,
        border: false,
        split: true,
        itemId: 'stakeholderGrid',
        store: 'StakeholderGrid',
        viewConfig: {
            stripeRows: false
        },
        columns: [
        {
            header: Lmkp.ts.msg('stakeholder-attr_name'),
            name: 'stakeholdernamecolumn',
            dataIndex: Lmkp.ts.msg('stakeholder-attr_name'),
            flex: 1,
//            sortable: true
        }, {
            header: Lmkp.ts.msg('stakeholder-attr_country'),
            name: 'stakeholdercountrycolumn',
            dataIndex: Lmkp.ts.msg('stakeholder-attr_country'),
            flex: 0,
//            sortable: true
        }, {
            xtype: 'templatecolumn',
            flex: 0,
            name: 'showDetailsColumn',
            width: 24,
            align: 'center',
            tpl: '<img src="static/img/information.png" style="cursor:pointer;" title="Show details">'
        }],
        dockedItems: [
        {
            xtype: 'toolbar',
            id: 'stakeholderGridTopToolbar',
            dock: 'top',
            items: ['->', {
                text: 'Clear selection',
                itemId: 'stakeholderResetSelectionButton'
            }, {
                text: 'Delete all filters',
                itemId: 'stakeholderDeleteAllFiltersButton'
            }]
        }]
    },{
        xtype: 'pagingtoolbar',
        id: 'stakeholderGridPagingToolbar',
        store: 'StakeholderGrid',
        dock: 'bottom',
        enableOverflow: false,
        displayInfo: true,
        beforePageText: Lmkp.ts.msg("activitypaging-before"),
        afterPageText: Lmkp.ts.msg("activitypaging-after"),
        displayMsg: Lmkp.ts.msg("stakeholder-paging_message"),
        emptyMsg: '<b>' + Lmkp.ts.msg("stakeholder-paging_empty") + '</b>'
    }]

});