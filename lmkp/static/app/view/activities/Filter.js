Ext.define('Lmkp.view.activities.Filter', {
    extend: 'Ext.panel.Panel',
    alias: ['widget.lo_editoractivityfilterpanel'],

    id: 'filterForm',
    flex: 0.5,
    border: 0,
    title: Lmkp.ts.msg("filter-title"),
    layout: {
        type: 'anchor'
    },
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
});
