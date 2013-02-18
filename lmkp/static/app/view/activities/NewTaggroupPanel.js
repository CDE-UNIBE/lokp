Ext.define('Lmkp.view.activities.NewTaggroupPanel', {
    extend: 'Ext.form.FieldContainer',
    alias: ['widget.lo_newtaggrouppanel'],

    layout: 'hbox',

    initComponent: function() {
        this.callParent(arguments);
        
        var me = this;

        var keyCb = Ext.create('Ext.form.field.ComboBox', {
            name: 'newtaggrouppanel_key',
            store: this.main_store,
            valueField: 'name',
            displayField: 'fieldLabel',
            queryMode: 'local',
            typeAhead: true,
            currentKey: this.initial_key,
            forceSelection: true,
            flex: 1,
            allowBlank: false,
            margin: '0 5 5 0',
            listeners: {
                select: function(combo, records) {
                    var newValue = records[0].get('name');
                    me.onKeyChanged(combo, newValue);
                }
            }
        });

        this.add(keyCb, {
            // Initial dummy TextField
            xtype: 'textfield',
            name: 'newtaggrouppanel_value',
            flex: 1,
            disabled: true,
            margin: '0 5 0 0'
        }, {
            // Button to delete attribute (disabled or not)
            xtype: 'button',
            name: 'deleteTag',
            text: Lmkp.ts.msg('button_delete'),
            disabled: !this.removable,
            handler: function() {
                me.onContainerRemoved();
            }
        });

        // Add an additional field to the right if provided
        if (this.right_field) {
            this.add(this.right_field);
        }

        // Set initial key
        if (this.initial_key) {
            // In order to set the right key, it is necessary to find it by
            // looking through the fieldLabels
            var r = this.main_store.findRecord('fieldLabel', this.initial_key);
            if (r) {
                this.getKeyField().setValue(r.get('name'));
                // The function setValue() does not trigger the 'select' event,
                // we need to fire it manually.
                keyCb.fireEvent('select', keyCb, [r]);
            } else {
                // If not yet found, try to find it through 'regular' field
                var r2 = this.main_store.findRecord('name', this.initial_key);
                if (r2) {
                    this.getKeyField().setValue(r2.get('name'));
                    // The function setValue() does not trigger the 'select'
                    // event, we need to fire it manually.
                    keyCb.fireEvent('select', keyCb, [r2]);
                }
            }
        }
    },

    // Before removing, add value to store again
    onContainerRemoved: function() {
        // add value (if selected) to store again
        var selectedKey = this.getKeyValue();
        if (selectedKey) {
            this.main_store.add(
                this.complete_store.findRecord('name', selectedKey)
            );
        }
        // remove fields
        this.removeAll(); // remove items first to allow form to check its validity
        this.destroy();
    },

    getKeyField: function() {
        var field = this.query('combobox[name=newtaggrouppanel_key]')[0];
        if (field) {
            return field;
        }
        return null;
    },

    getKeyValue: function() {
        var value = this.getKeyField();
        if (value) {
            return value.getSubmitValue();
        }
        return null;
    },
    
    getInitialKey: function() {
        return this.initial_key;
    },

    getValueField: function() {
        var field = this.query('[name=newtaggrouppanel_value]')[0];
        if (field) {
            return field;
        }
        return null;
    },

    getValueValue: function() {
        var value = this.getValueField();
        // Treat empty string as null value
        if (value && value.getValue() != '') {
            return value.getSubmitValue();
        }
        return null;
    },

    getInitialValue: function() {
        return this.initial_value;
    },

    getInitialTagId: function() {
        return this.initial_tagid;
    },

    isMainTag: function() {
        return this.is_maintag;
    },

    onKeyChanged: function(combobox, newValue) {
        if (combobox && newValue) {
            // Remove existing filters on combobox (by type-ahead)
            var store = combobox.getStore();
            if (store) {
                store.clearFilter();
            }
            // Remove newly selected value from store
            var currentRecord = this.main_store.findRecord('name', newValue);
            if (currentRecord) {
                this.main_store.remove(currentRecord);
                if (combobox.currentKey != newValue) {
                    // Add previously selected (now deselected) value to store again
                    var previousRecord = this.complete_store.findRecord(
                        'name', combobox.currentKey);
                    if (previousRecord) {
                        this.main_store.add(previousRecord.copy());
                        this.main_store.sort('fieldLabel', 'ASC');
                    }
                    // Store value to combobox
                    combobox.currentKey = newValue;
                }
                // Replace the value field
                this.items.getAt(
                    this.items.findIndex('name', 'newtaggrouppanel_value')
                ).destroy();

                var newField = this.getNewValueField(currentRecord);
                if (this.initial_value && !this.initial_value_set) {
                    // If it is a combobox and in order to set the right value,
                    // it is necessary to find it by looking through field2
                    if (newField.getXType() == 'combobox') {
                        var r = newField.getStore().findRecord('field2',
                            this.initial_value);
                        if (r) {
                            newField.setValue(r.get('field1'));
                        }
                    } else {
                        newField.setValue(this.initial_value);
                    }
                    // Set it only once
                    this.initial_value_set = true;
                }
                this.insert(1, newField);
            }
        }
    },

    getNewValueField: function(record) {

        // try to find categories
        var selectionValues = record.get('store');
        if (selectionValues) {      // categories of possible values available, create ComboBox
            var valueField = Ext.create('Ext.form.field.ComboBox', {
                name: 'newtaggrouppanel_value',
                store: selectionValues,
                queryMode: 'local',
                editable: true,
                forceSelection: true,
                margin: '0 5 0 0'
            });
        } else {                    // no categories available, create field based on xtype
            switch (record.get('xtype')) {
                case "numberfield":
                    var valueField = Ext.create('Ext.form.field.Number', {
                        name: 'newtaggrouppanel_value',
                        margin: '0 5 0 0'
                    });
                    // add validation if available
                    if (record.get('validator')) {
                        valueField.validator = new Function('value', record.get('validator'));
                    }
                    break;
                case "datefield":
                    var valueField = Ext.create('Ext.form.field.Date', {
                        name: 'newtaggrouppanel_value',
                        margin: '0 5 0 0',
                        format: 'd.m.Y',
                        emptyText: Lmkp.ts.msg('input-validation_date-format'),
                        invalidText: Lmkp.ts.msg('input-validation_invalid-date')
                    });
                    // Add validation if available
                    if (record.get('validator')) {
                        valueField.validator = new Function('value', record.get('validator'));
                    }
                    break;
                default:
                    var valueField = Ext.create('Ext.form.field.Text', {
                        name: 'newtaggrouppanel_value',
                        margin: '0 5 0 0'
                    });
                    // add validation if available
                    if (record.get('validator')) {
                        valueField.validator = new Function('value', record.get('validator'));
                    }
                    break;
            }
        }
        valueField.flex = 1;
        return valueField;
    }

});