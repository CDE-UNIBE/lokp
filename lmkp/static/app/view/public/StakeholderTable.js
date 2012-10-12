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
        title: Lmkp.ts.msg('stakeholders_title'),
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
            header: Lmkp.ts.msg('stakeholder_db-key-name'),
            name: 'stakeholdernamecolumn',
            dataIndex: Lmkp.ts.msg('stakeholder_db-key-name'),
            flex: 1,
//            sortable: true
        }, {
            header: Lmkp.ts.msg('stakeholder_db-key-country'),
            name: 'stakeholdercountrycolumn',
            dataIndex: Lmkp.ts.msg('stakeholder_db-key-country'),
            flex: 0,
//            sortable: true
        }, {
            xtype: 'templatecolumn',
            flex: 0,
            name: 'showDetailsColumn',
            width: 24,
            align: 'center',
            tpl: '<img src="static/img/information.png" style="cursor:pointer;" title="' + Lmkp.ts.msg('gui_show-details') + '">'
        }],
        dockedItems: [
        {
            xtype: 'toolbar',
            id: 'stakeholderGridTopToolbar',
            dock: 'top',
            items: ['->', {
                text: Lmkp.ts.msg('gui_clear-selection'),
                itemId: 'stakeholderResetSelectionButton'
            }, {
                text: Lmkp.ts.msg('gui_delete-all-filters'),
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
        beforePageText: Lmkp.ts.msg('gui_paging-before'),
        afterPageText: Lmkp.ts.msg('gui_paging-after'),
        displayMsg: Lmkp.ts.msg('stakeholders_paging-message'),
        emptyMsg: '<b>' + Lmkp.ts.msg('stakeholders_paging-empty') + '</b>'
    }]

});