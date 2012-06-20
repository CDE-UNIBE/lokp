Ext.define('Lmkp.view.Stakeholder',{
    extend: 'Ext.panel.Panel',
    alias: ['widget.stakeholderpanel'],

    items:[{
        // grid columns
        columns: [{
            header: Lmkp.ts.msg("stakeholder-name"),
            itemId: 'stakeholder-name-column',
            dataIndex: Lmkp.ts.msg("stakeholder-name"),
            flex: 1,
            sortable: true
        }],
        dockedItems: [{
            dock: 'bottom',
            itemId: 'strakeholder-grid-paging-toolbar',
            enableOverflow: false,
            displayInfo: true,
            beforePageText: Lmkp.ts.msg("activitypaging-before"),
            afterPageText: Lmkp.ts.msg("activitypaging-after"),
            displayMsg: Lmkp.ts.msg("activitypaging-message"),
            emptyMsg: '<b>' + Lmkp.ts.msg("activitypaging-empty") + '</b>',
            store: 'StakeholderGrid',
            xtype: 'pagingtoolbar'
        }],
        itemId: 'stakeholders-grid',
        split: true,
        store: 'StakeholderGrid',
        viewConfig: {
            stripeRows: false
        },
        xtype: 'gridpanel'
    }],
    title: Lmkp.ts.msg("Stakeholders")
})