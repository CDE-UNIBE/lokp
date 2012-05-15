Ext.define('Lmkp.view.activities.NewActivityWindow', {
	extend: 'Ext.window.Window',
	
	title: 'Add new Activity',
	
	layout: 'fit',
	defaults: {
		border: 0
	},
	width: 400,

	initComponent: function() {
		
		// prepare the form
		var form = Ext.create('Ext.form.Panel', {
			border: 0,
			bodyPadding: 5,
			layout: 'anchor',
			defaults: {
				anchor: '100%'
			},
			buttons: [{
				formBind: true,
				disabled: true,
				text: 'Submit',
				handler: function() {
					var theform = this.up('form').getForm();
					if (theform.isValid()) {
						
						// The form cannot be submitted 'normally' because ActivityProtocol expects a JSON object.
						// As a solution, the form values are used to create a JSON object which is sent using an
						// AJAX request.
						// http://www.sencha.com/forum/showthread.php?132082-jsonData-in-submit-action-of-form

						// collect values and fill them into TagGroups
						// TODO: it seems that the main tag (first added to dict) always remains in first position, but
						// maybe this should be ensured in a better way ...
						var taggroups = [];
						var activities = [];
						
						for (var i in form.getValues()) {
							var tags = [];
							var main_tag = {};
							// first, look only at mandatory fields (no '__val' or '__attr' in name)
							if (i.indexOf("__attr") == -1 && i.indexOf("__val") == -1) {
								var tag = {};
								tag['key'] = i;
								tag['value'] = form.getValues()[i];
								tag['op'] = 'add';
								tags.push(tag);
								// also add to main_tag
								main_tag['key'] = i;
								main_tag['value'] = form.getValues()[i];
								
								// look if further attributes to this field were entered
								var attrs = Ext.ComponentQuery.query('[name=' + i + '__attr]');
								var vals = Ext.ComponentQuery.query('[name=' + i + '__val]');
								if (attrs.length > 0 && vals.length > 0 && attrs.length == vals.length) {
									for (var j=0; j<attrs.length; j++) {
										var tag = {};
										tag['key'] = attrs[j].getValue();
										tag['value'] = vals[j].getValue();
										tag['op'] = 'add';
										tags.push(tag);
									}
								}
							}
							if (tags.length > 0) {
								taggroups.push({'tags': tags, 'main_tag': main_tag});
							}
						}
						var diffObject = {'activities': [{'taggroups': taggroups}]};

						// send JSON through AJAX request
						Ext.Ajax.request({
							url: '/activities',
							method: 'POST',
							headers: {'Content-Type': 'application/json;charset=utf-8'},
							jsonData: diffObject,
							success: function() {
								Ext.Msg.alert('Success', 'The activity was successfully created. It will be reviewed shortly.');
								form.up('window').close();
							},
							failure: function() {
								Ext.Msg.alert('Failure', 'The activity could not be created.');
							}
						});
					}
				}
			}]
		});
		
		// load a store containing only the mandatory fields.
		var mandatoryStore = Ext.create('Lmkp.store.Config');
    	mandatoryStore.filter("allowBlank", false);
    	mandatoryStore.load();
    	
    	// load a store containing only the optional fields. 
    	// This is needed to keep track of all the optional fields available.
    	var optionalStore_complete = Ext.create('Lmkp.store.Config');
		// for some reason, 'normal' filtering of stores does not work (asynchronous problem?)
		// instead, 'filtering' is done manually
		optionalStore_complete.on('load', function(store) {
			store.each(function(record) {
				if (record.get('allowBlank') != true) {
					store.remove(record);
				}
			});
		});
		optionalStore_complete.load();

		// create a field for each mandatory attribute.
		mandatoryStore.on('load', function(store) {
			store.each(function(record) {
				form.up('window')._getFormField(form, record, optionalStore_complete);
			});
		});
		
		this.items = form;

		this.callParent(arguments);
	},
	
	/**
	 * Adds a form field to 'form' for each 'record'.
	 */
	_getFormField: function(form, record, optionalStore_complete) {
		
		// FieldContainer is needed for nice layout
		var fieldContainer = Ext.create('Ext.form.FieldContainer', {
			layout: 'hbox'
		});
		
		// add field (TextField, NumberField or ComboBox) to FieldContainer
		if (record.get('store') == '') {
			// no predefined values, create TextField or NumberField (with validation)
			switch (record.get('xtype')) {
	        	case "numberfield":
	                var valueField = Ext.create('Ext.form.field.Number', {
	                	flex: 1,
	                    margin: '0 5 0 0',
	                    name: record.get('name'),
	                    allowBlank: record.get('allowBlank')
	                });
	                // add validation if available
	                if (record.get('validator')) {
	                	valueField.validator = new Function('value', record.get('validator'));
	                }
	                break;
	            default:
	                var valueField = Ext.create('Ext.form.field.Text', {
	                	flex: 1,
	                    margin: '0 5 0 0',
	                    name: record.get('name'),
	                    allowBlank: record.get('allowBlank')
	                });
	                // add validation if available
	                if (record.get('validator')) {
	                	valueField.validator = new Function('value', record.get('validator'));
	                }
	                break;
            }
			fieldContainer.add(valueField);
		} else {
			// predefined values available, add ComboBox
			fieldContainer.add({
				flex: 1,
				margin: '0 5 0 0',
				xtype: record.get('xtype'),
				name: record.get('name'),
				store: record.get('store'),
				allowBlank: record.get('allowBlank'),
				editable: false,
				forceSelection: true
			});
		}
		
		// add Button to show further attributes
		fieldContainer.add({
			xtype: 'button',
			name: record.get('name') + '__btn',
			text: '+',
			handler: function() {
				// create store to keep track of already selected attributes
				var optionalStore = Ext.create('Lmkp.store.Config');
				// again, 'normal' filtering of stores does not work (asynchronous problem?)
				optionalStore.on('load', function(store) {
					store.each(function(record) {
						if (record.get('allowBlank') != true) {
							store.remove(record);
						}
					});
				});
				optionalStore.load();

				// populate Panel that allows selecting additional attributes
				var additionalPanel = Ext.ComponentQuery.query('panel[name=' + record.get('name') + ']')[0];
				this.up('window')._addOptionalFields(additionalPanel, optionalStore, optionalStore_complete);
				
				// disable button if clicked
				this.disable();
			}
		});
		
		// put it all together and add it to form
		form.add({
			xtype: 'fieldset',
			title: record.get('fieldLabel'),
			layout: 'anchor',
			defaults: {
				anchor: '100%'
			},
			border: 1,
			items: [
				fieldContainer,
				{
					// initially hidden panel for additional attributes
					xtype: 'panel',
					name: record.get('name'),
					hidden: true,
					border: 0,
					layout: 'anchor',
					defaults: {
						anchor: '100%'
					}
				}
			]
		});
		
	},
	
	/**
	 * Adds additional ComboBoxes to a 'panel'. Every record in 'store' can only be selected once. 
	 */
	_addOptionalFields: function(panel, store, store_complete) {

		// create ComboBox
		var cb = Ext.create('Ext.form.field.ComboBox', {
			flex: 1,
			name: panel.name + '__attr',
			store: store,
			valueField: 'name',
			displayField: 'fieldLabel',
			queryMode: 'local',
			forceSelection: true,
			editable: false,
			allowBlank: false,
			margin: '0 5 0 0',
			listeners: {
				// handle actions when selection changed
				change: function(combo, newValue, oldValue, eOpts) {
					// remove newly selected value from store
					var currentRecord = store.findRecord('name', newValue);
					store.remove(currentRecord);
					// add previously selected (now deselected) value to store again
					var previousRecord = store_complete.findRecord('name', oldValue);
					if (previousRecord) {
						store.add(previousRecord);
					}
					// replace value field
					var name_valueField = panel.name + '__val';
					var index_valueField = fieldContainer.items.findIndex('name', name_valueField);
					fieldContainer.items.getAt(index_valueField).destroy();
					var newField = this.up('window')._getValueField(currentRecord, name_valueField);
					fieldContainer.insert(index_valueField, newField);
					// enable 'add' button if there are further optional attributes remaining
					if (store.data.getCount() > 0) {
						button_add.enable();
					}
				}
			}
		});
		
		// create Button to add more attributes
		var button_add = Ext.create('Ext.button.Button', {
			margin: '0 5 0 0',
			text: '+',
			name: 'button_add',
			disabled: true,
			handler: function() {
				// add another field
				this.up('window')._addOptionalFields(this.up('panel'), store, store_complete);
				// disable button
				this.disable();
			}
		});
		
		// create Button to remove attributes
		var button_remove = Ext.create('Ext.button.Button', {
			text: '-',
			name: 'button_remove',
			handler: function() {
				var fieldContainer = this.up('fieldcontainer');
				// add value (if selected) to store again
				var selectedValue = cb.getValue();
				if (selectedValue) {
					store.add(store_complete.findRecord('name', selectedValue));
				}
				// remove fields
				fieldContainer.removeAll(); // remove items first to allow form to check its validity
				fieldContainer.destroy();
				// re-enable previous button to add further attributes
				var previousFieldset = panel.items.last();
				if (previousFieldset) {
					var btn = previousFieldset.items.getAt(previousFieldset.items.findIndex('name', 'button_add'))
					btn.enable();
				} else {
					// re-enable first button if all additional attributes were removed
					var buttons = Ext.ComponentQuery.query('button[name=' + panel.name + '__btn]');
					if (buttons) {
						buttons[0].enable();
					}
				}
			}
		});
		
		// create initial dummy TextField (disabled)
		var valueField = Ext.create('Ext.form.field.Text', {
			name: panel.name + '__val',
			disabled: true,
			margin: '0 5 0 0'
		});

		// put it all together in a FieldContainer for nice display
		var fieldContainer = Ext.create('Ext.form.FieldContainer', {
			layout: 'hbox',
			items: [cb, valueField, button_add, button_remove]
		});

		// add all to panel and display it
		panel.setVisible(true);
		panel.add(fieldContainer);
	},
	
	/**
	 * Returns a value field (ComboBox, NumberField or TextField)
	 */
	_getValueField: function(record, fieldName) {
		// try to find categories
        var selectionValues = record.get('store');
        if (selectionValues) {      // categories of possible values available, create ComboBox
            var valueField = Ext.create('Ext.form.field.ComboBox', {
                name: fieldName,
                store: selectionValues,
                queryMode: 'local',
                editable: false,
                value: selectionValues[0],
                margin: '0 5 0 0',
                allowBlank: false
            });
        } else {                    // no categories available, create field based on xtype
            switch (record.get('xtype')) {
                case "numberfield":
                    var valueField = Ext.create('Ext.form.field.Number', {
                        name: fieldName,
                        margin: '0 5 0 0',
                        allowBlank: false
                    });
                    // add validation if available
                    if (record.get('validator')) {
                    	valueField.validator = new Function('value', record.get('validator'));
                    }
                    break;
                default:
                    var valueField = Ext.create('Ext.form.field.Text', {
                        name: fieldName,
                        margin: '0 5 0 0',
                        allowBlank: false
                    });
                    // add validation if available
                    if (record.get('validator')) {
                    	valueField.validator = new Function('value', record.get('validator'));
                    }
                    break;
            }
        }
        return valueField;
	}
});
