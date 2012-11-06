Ext.define('Lmkp.view.activities.Filter', {
    extend: 'Ext.panel.Panel',
    alias: ['widget.lo_activityfilterpanel'],

    id: 'activityFilterForm',
    flex: 0.5,
    border: 0,
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
            store: [
                ['and', Lmkp.ts.msg('filter_logical-operator-and')],
                ['or', Lmkp.ts.msg('filter_logical-operator-or')]
            ],
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
            item_type: 'activity'
        }, {
            xtype: 'button',
            name: 'addTimeFilter',
            text: Lmkp.ts.msg('button_add-time-filter'),
            tooltip: Lmkp.ts.msg('tooltip_add-time-filter'),
            iconCls: 'toolbar-button-add',
            flex: 0,
            item_type: 'activity'
        }]
    }],

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
