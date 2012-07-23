Ext.define('Lmkp.view.editor.StakeholderTable', {
    extend: 'Ext.panel.Panel',
    alias: ['widget.lo_editorstakeholdertablepanel'],

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
        }, {
            xtype: 'gridpanel',
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
                    sortable: true
                }, {
                    header: Lmkp.ts.msg('stakeholder-attr_country'),
                    name: 'stakeholdercountrycolumn',
                    dataIndex: Lmkp.ts.msg('stakeholder-attr_country'),
                    flex: 0,
                    sortable: true
                }
            ],
            dockedItems: [
                {
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
                }
            ]
        }
    ]

});