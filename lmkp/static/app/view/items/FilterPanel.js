Ext.define('Lmkp.view.items.FilterPanel', {
    extend: 'Ext.panel.Panel',
    alias: ['widget.lo_itemsfilterpanel'],

    border: 0,
    layout: {
        type: 'hbox',
        flex: 'stretch'
    },

    initComponent: function() {

        this.items = [];

        if (this.filterField) {
            this.items.push(this.filterField);
        }

        this.items.push({
            // empty panel for spacing
            xtype: 'panel',
            flex: 1,
            border: 0
        }, {
            xtype: 'button',
            name: 'filterActivateButton',
            text: Lmkp.ts.msg('button_filter-activate'),
            tooltip: Lmkp.ts.msg('tooltip_filter-activate'),
            iconCls: 'toolbar-button-accept',
            enableToggle: true,
            flex: 0,
            margin: '0 5 0 0'
        }, {
            xtype: 'button',
            name: 'deleteButton',
            text: Lmkp.ts.msg('button_filter-delete'),
            tooltip: Lmkp.ts.msg('tooltip_filter-delete'),
            iconCls: 'toolbar-button-delete',
            enableToggle: false,
            flex: 0
        });

        this.callParent(arguments);
    },

    getFilterValues: function() {
        if (this.filterIsActivated()) {
            if (this.name == 'attributePanel') {
                var attr = this.down('combobox[name=attributeCombo]');
                var op = this.down('combobox[name=filterOperator]');
                var value = this.down('[name=valueField]');
                return {
                    attr: attr.getValue(),
                    op: op.getValue(),
                    value: value.getValue()
                };
            } else if (this.name == 'timePanel') {
                var date = this.down('datefield[name=dateField]');
                return {
                    date: Ext.Date.format(date.getValue(), "Y-m-d H:i:s.u")
                }
            }
        }
    },

    filterIsActivated: function() {
        var button = this.down('button[name=filterActivateButton]');
        if (button) {
            return button.pressed;
        }
        return false;
    },

    deactivateFilter: function() {
        var button = this.down('button[name=filterActivateButton]');
        if (button) {
            button.toggle(false);
        }
    }
});