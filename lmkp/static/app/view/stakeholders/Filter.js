Ext.define('Lmkp.view.stakeholders.Filter', {
    extend: 'Ext.panel.Panel',
    alias: ['widget.lo_stakeholderfilterpanel'],

    id: 'stakeholderFilterForm',
    flex: 0.5,
    border: 0,
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
                    fieldLabel: Lmkp.ts.msg('filter_logical-operator'),
                    flex: 0
                }, {
                    xtype: 'panel', // empty panel for spacing
                    flex: 1,
                    border: 0
                }, {
                    xtype: 'button',
                    name: 'addAttributeFilter',
                    text: Lmkp.ts.msg('button_add-attribute-filter'),
                    tooltip: Lmkp.ts.msg('tooltip_add-attribute-filter'),
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
            var v = filterpanels[i].getFilterValues();
            if (v) {
                ret.push(v);
            }
        }
        return ret;
    },

    toggleLogicalOperator: function() {
        var filterpanels = this.query('lo_itemsfilterpanel[name=attributePanel]');
        var cb = this.down('combobox[name=logicalOperator]');
        if (cb && filterpanels) {
            cb.setVisible(filterpanels.length > 1);
        }
    },

    getLogicalOperator: function() {
        var cb = this.down('combobox[name=logicalOperator]');
        if (cb) {
            return cb.getValue();
        }
        return null;
    }
});