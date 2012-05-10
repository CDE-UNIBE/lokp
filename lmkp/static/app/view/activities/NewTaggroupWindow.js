Ext.define('Lmkp.view.activities.NewTaggroupWindow', {
	extend: 'Ext.window.Window',
	
	layout: 'fit',
	defaults: {
		border: 0
	},
	width: 400,
	
	initComponent: function() {
		var me = this;
		
		// set window title
		var action = (me.selected_taggroup) ? 'Change' : 'Add';
		this.title = action + ' information';
		
		if (me.activity_id) {
			// prepare the form
			var form = Ext.create('Ext.form.Panel', {
				border: 0,
				bodyPadding: 5,
				layout: 'anchor',
				defaults: {
					anchor: '100%'
				},
				items: [{
					// submit activity_identifier as well
					xtype: 'hiddenfield',
					name: 'activity_identifier',
					value: me.activity_id
				}, {
					// button to add new attribute selection to form
					xtype: 'panel',
					layout: {
						type: 'hbox',
						flex: 'stretch'
					},
					border: 0,
					items: [{
						// empty panel for spacing
						xtype: 'panel',
						flex: 1,
						border: 0
					}, {
						// the button
						xtype: 'button',
						text: '[+] Add item',
						flex: 0,
						handler: function() {
							// functionality to add new attribute selection to form
							// it is a main_tag if it is the first ComboBox of the form
							var main_tag = Ext.ComponentQuery.query('combobox[name=tg_combobox_maintag]').length == 0 && Ext.ComponentQuery.query('combobox[name=tg_combobox]').length == 0;
							var fieldContainer = form.up('window')._getFieldContainer(store, completeStore, true, main_tag, null, null);
							form.insert(form.items.length-1, fieldContainer);
						}
					}]
				}],
				// submit button
				buttons: [{
					formBind: true,
					disabled: true,
					text: 'Submit',
					handler: function() {
						var theform = form.getForm();
						if (theform.isValid()) {
							// submit functionality. collect values first
							var main_tag = null;
							var tags = []
							
							var attr_maintag = Ext.ComponentQuery.query('combobox[name=tg_combobox_maintag]');
							var val_maintag = Ext.ComponentQuery.query('[name=tg_valuefield_maintag]');
							if (attr_maintag.length > 0 && val_maintag.length > 0) {
								main_tag = attr_maintag[0].getValue();
								// add main_tag to tags as well
								tags.push({
									'key': attr_maintag[0].getValue(),
									'value': val_maintag[0].getValue()
								});
							}
							
							var attrs = Ext.ComponentQuery.query('combobox[name=tg_combobox]');
							var values = Ext.ComponentQuery.query('[name=tg_valuefield]');
							if (attrs.length > 0 && values.length > 0 && attrs.length == values.length) {
								for (var i=0; i<attrs.length; i++) {
									tags.push({
										'key': attrs[i].getValue(),
										'value': values[i].getValue()
									});
								}
							}
							
							console.log(main_tag)
							console.log(tags);
							
							/*
							var attrs = Ext.ComponentQuery.query('combobox[name=tg_combobox]');
							var values = Ext.ComponentQuery.query('[name=tg_valuefield]');
							var taggroup = {}
							if (attrs.length > 0 && values.length > 0 && attrs.length == values.length) {
								for (var i=0; i<attrs.length; i++) {
									taggroup[attrs[i].getValue()] = values[i].getValue()
								}
								
								var all_taggroups = [];
								var tg = me.activity.taggroups();
								tg.each(function () {
									// console.log(this.data);
									var to_add= {}
									for (var el in this.data) {
										console.log(el);
										if (el != 'lmkp.model.activity_id') {
											// do something
										}
									}
									all_taggroups.push(this.data);
								});
								// add new taggroup
								all_taggroups.push(taggroup);
								console.log(all_taggroups);
								
								// for the moment being, create dummy geometry
								var geometry = {'type': 'POINT', 'coordinates': [46.951081, 7.438637]}
								
								// put JSON together (all attributes form one TagGroup), also add previous TagGroups
								var jsonData = {'data': [{'geometry': geometry, 'taggroups': all_taggroups, 'id': form.getValues().activity_identifier}]}
								console.log(jsonData);
								
								// send JSON through AJAX request
								// Ext.Ajax.request({
									// url: '/activities',
									// method: 'POST',
									// heades: {'Content-Type': 'application/json;charset=utf-8'},
									// jsonData: jsonData,
									// success: function(response, options) {
										// console.log(response);
										// Ext.Msg.alert('Success', 'The information was successfully submitted. It will be reviewed shortly.');
										// form.up('window').close();
									// },
									// failure: function(response, options) {
										// Ext.Msg.alert('Failure', 'The information could not be submitted.');
									// }
								// });
							}
							*/
						}
					}
				}]
			});
			
			// load the config store
			var store = Ext.create('Lmkp.store.Config');
			store.load();
			// another instance of the config store is needed to keep track of all attributes available
			var completeStore = Ext.create('Lmkp.store.Config');
			completeStore.load();
			
			// if a TagGroup was selected to edit, show its values
			if (me.selected_taggroup) {
				var tags = me.selected_taggroup.tags();
				
				// find main_tag, display it and remove it from store
				var main_tag_index = tags.find('id', me.selected_taggroup.get('main_tag'));
				if (main_tag_index != -1) {
					var fieldContainer = this._getFieldContainer(store, completeStore, true, true, tags.getAt(main_tag_index).get('key'), tags.getAt(main_tag_index).get('value')); 
					form.insert(1, fieldContainer);
					tags.removeAt(main_tag_index);
				}
				
				// display all other tags
				tags.each(function(record) {
					var fieldContainer = me._getFieldContainer(store, completeStore, true, false, record.get('key'), record.get('value'));
					form.insert(1, fieldContainer);
				});
				
			} else {
			// if no TagGroup was selected to edit, show initial attribute selection
				var fieldContainer = this._getFieldContainer(store, completeStore, false, true);
				form.insert(1, fieldContainer);
			}

			// add form to window
			this.items = form;
		}
		this.callParent(arguments);
	},
	
	/**
	 * Returns a FieldContainer with a ComboBox for attribute selection.
	 * 'store' is needed to display only attributes that are not yet selected
	 * 'completeStore' keeps track of all attributes available
	 * 'removable' indicates whether delete-button is disabled or not
	 * 'main_tag' indicates whether it is main_tag or not
	 */
	_getFieldContainer: function(store, completeStore, removable, main_tag, initialAttribute, initialValue) {
		
		var cb_name = (main_tag) ? 'tg_combobox_maintag' : 'tg_combobox';

		// ComboBox to select attribute
		var cb = Ext.create('Ext.form.field.ComboBox', {
			xtype: 'combobox',
			name: cb_name,
			store: store,
			valueField: 'name',
			displayField: 'fieldLabel',
			queryMode: 'local',
			typeAhead: true,
			forceSelection: true,
			flex: 1,
			allowBlank: false,
			margin: '0 5 5 0',
			listeners: {
				// functionality to replace value field based on selected attribute
				change: function(combo, newValue, oldValue, eOpts) {
					// remove newly selected value from store
					var currentRecord = store.findRecord('name', newValue);
					store.remove(currentRecord);
					// add previously selected (now deselected) value to store again
					var previousRecord = completeStore.findRecord('name', oldValue);
					if (previousRecord) {
						store.add(previousRecord);
					}
					// replace the value field
					fieldContainer.items.getAt(fieldContainer.items.findIndex('name', 'tg_valuefield')).destroy();
					var newField = this.up('window')._getValueField(currentRecord, main_tag);
					// if initialValue was provided (when editing selected TagGroup), then show its value
					if (initialValue) {
						newField.setValue(initialValue);
					}
					fieldContainer.insert(1, newField);
				}
			}
		});
		// if initialAttribute was provided (when editing selected TagGroup), then show its value
		if (initialAttribute) {
			cb.setValue(initialAttribute);
		}
		
		// put together the FieldContainer
		var fieldContainer = Ext.create('Ext.form.FieldContainer', {
			layout: 'hbox',
			items: [
				cb
			, {
				// initial dummy TextField (disabled)
				xtype: 'textfield',
				name: 'tg_valuefield',
				flex: 1,
				disabled: true,
				margin: '0 5 0 0'
			}, {
				// button to delete attribute (disabled or not)
				xtype: 'button',
				text: '[-] Delete',
				disabled: !removable,
				handler: function() {
					// functionality to remove attribute
					var fieldContainer = this.up('fieldcontainer');
					// add value (if selected) to store again
					var selectedValue = fieldContainer.items.getAt(fieldContainer.items.findIndex('name', 'tg_combobox')).getValue();
					if (selectedValue) {
						store.add(completeStore.findRecord('name', selectedValue));
					}
					// remove fields
					fieldContainer.removeAll(); // remove items first to allow form to check its validity
					fieldContainer.destroy();
				}
			}]
		});

		return fieldContainer;
	},
	
	/**
	 * Returns a form field (ComboBox, NumberField or TextField)
	 * Basically the same as in controller.Filter)
	 */
	_getValueField: function(record, main_tag) {
		
		var fieldName = (main_tag) ? 'tg_valuefield_maintag' : 'tg_valuefield';
		
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
    },
});
