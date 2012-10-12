Ext.define('Lmkp.view.activities.NewTaggroupPanel', {
    extend: 'Ext.form.FieldContainer',
    alias: ['widget.lo_newtaggrouppanel'],

    layout: 'hbox',

    initComponent: function() {
        this.callParent(arguments);
        
        var me = this;

        this.add({
            xtype: 'combobox',
            name: 'newtaggrouppanel_key',
            store: this.main_store,
            valueField: 'name',
            displayField: 'fieldLabel',
            queryMode: 'local',
            readOnly: this.is_mandatory,
            editable: false,
//            typeAhead: true,
            forceSelection: true,
            flex: 1,
            allowBlank: false,
            margin: '0 5 5 0',
            listeners: {
                change: function(combo, newValue, oldValue, eOpts) {
                    me.onKeyChanged(oldValue, newValue);
                }
            }
        }, {
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
            this.getKeyField().setValue(this.initial_key);
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
            return value.getValue();
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
        if (value) {
            return value.getValue();
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

    // Replace value field based on selected attribute
    onKeyChanged: function(oldValue, newValue) {

        if (newValue) {
            // remove newly selected value from store
            var currentRecord = this.main_store.findRecord('name', newValue);
            if (currentRecord) {
                this.main_store.remove(currentRecord);

                // add previously selected (now deselected) value to store again
                var previousRecord = this.complete_store.findRecord('name', oldValue);
                if (previousRecord) {
                    this.main_store.add(previousRecord);
                }
                // replace the value field
                this.items.getAt(
                    this.items.findIndex('name', 'newtaggrouppanel_value')
                ).destroy();

                var newField = this.getNewValueField(currentRecord);
                if (this.initial_value && !this.initial_value_set) {
                    // Set initial value (set it only once)
                    newField.setValue(this.initial_value);
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