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
                header: Lmkp.ts.msg('gui_id'),
                name: 'stakeholderIdentifierColumn',
                dataIndex: 'id',
                flex: 0,
                sortable: false
            }, {
                header: Lmkp.ts.msg('gui_last-change'),
                name: 'stakeholderLastChangeColumn',
                dataIndex: 'timestamp',
                flex: 0,
                sortable: false,
                hidden: true
            }, {
                header: Lmkp.ts.msg('stakeholder_db-key-name'),
                name: 'stakeholderNameColumn',
                dataIndex: Lmkp.ts.msg('stakeholder_db-key-name'),
                flex: 1,
                sortable: false // TODO!
            }, {
                header: Lmkp.ts.msg('stakeholder_db-key-countryoforigin'),
                name: 'stakeholderCountryOfOriginColumn',
                dataIndex: Lmkp.ts.msg('stakeholder_db-key-countryoforigin'),
                flex: 0,
                sortable: false // TODO!
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