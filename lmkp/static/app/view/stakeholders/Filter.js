Ext.define('Lmkp.view.stakeholders.Filter', {
    extend: 'Ext.panel.Panel',
    alias: ['widget.lo_editorstakeholderfilterpanel'],

    id: 'stakeholderFilterForm',
    flex: 0.5,
    border: 0,
    title: Lmkp.ts.msg('filter-stakeholder_title'),
    layout: {
        type: 'anchor'
    },
    defaults: {
        anchor: '100%',
        border: 0
    },
    bodyPadding: 5,
    items: [
        {
            xtype: 'panel',
            layout: {
                type: 'hbox',
                flex: 'stretch'
            },
            items: [
                {
                    xtype: 'combobox',
                    store: ['and', 'or'],
                    name: 'logicalOperator',
                    value: 'and',
                    editable: false,
                    hidden: true,
                    fieldLabel: 'Logical operator',
                    flex: 0
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
                    flex: 0,
                    item_type: 'stakeholder'
                }
            ]
        }
    ],

    getFilterItems: function() {
        var ret = [];
        var filterpanels = this.query('lo_itemsfilterpanel');
        for (var i in filterpanels) {
            ret.push(filterpanels[i].getFilterValues());
        }
        return ret;
    }
});