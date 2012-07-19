Ext.define('Lmkp.view.activities.NewTaggroupWindow', {
    extend: 'Ext.window.Window',
	
    layout: 'fit',
    defaults: {
        border: 0
    },
    width: 400,
	
    // needed to keep track of original tags
    old_tags: [],
    old_main_tag: null,
	
    initComponent: function() {
		
        var me = this;
        // 'reset' original tracks
        me.old_tags = [];
        me.old_main_tag = null;

        // set window title
        var action = (me.selected_taggroup) ? 'Change' : 'Add';
        this.title = action + ' information';
		
        if (me.activity_id && me.version) {
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
                    // submit version as well
                    xtype: 'hiddenfield',
                    name: 'version',
                    value: me.version
                }, {
                    // button to add new attribute selection to form
                    xtype: 'lo_panel',
                    layout: {
                        type: 'hbox',
                        flex: 'stretch'
                    },
                    border: 0,
                    items: [{
                        // empty panel for spacing
                        xtype: 'lo_panel',
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
                            var main_tag = {};
                            var newTags = [];
                            var deleteTags = [];
							
                            // main tag
                            var attr_maintag = Ext.ComponentQuery.query('combobox[name=tg_combobox_maintag]');
                            var val_maintag = Ext.ComponentQuery.query('[name=tg_valuefield_maintag]');
                            if (attr_maintag.length > 0 && val_maintag.length > 0) {
                                // always add latest version as new main tag
                                main_tag['key'] = attr_maintag[0].getValue();
                                main_tag['value'] = val_maintag[0].getValue();
								
                                // check for changes in main tag
                                if (!attr_maintag[0].oldAttribute) {
                                    // brand new main tag (new key and new value)
                                    // collect data to 'delete' old main tag (if available)
                                    if (me.old_main_tag) {
                                        deleteTags.push({
                                            'key': me.old_main_tag.get('key'),
                                            'value': me.old_main_tag.get('value'),
                                            'id': me.old_main_tag.get('id'),
                                            'op': 'delete'
                                        });
                                    }
                                    // collect data to 'add' new main tag
                                    newTags.push({
                                        'key': attr_maintag[0].getValue(),
                                        'value': val_maintag[0].getValue(),
                                        'op': 'add'
                                    });
                                } else {
                                    // main tag existed already
                                    if (attr_maintag[0].oldAttribute != attr_maintag[0].getValue()) {
                                        // main tag has changed (new key and new value)
                                        // collect data to 'delete' old main tag
                                        deleteTags.push({
                                            'key': attr_maintag[0].oldAttribute,
                                            'value': me.old_main_tag.get('value'),
                                            'id': me.old_main_tag.get('id'),
                                            'op': 'delete'
                                        });
                                        // collect data to 'add' new main tag
                                        newTags.push({
                                            'key': attr_maintag[0].getValue(),
                                            'value': val_maintag[0].getValue(),
                                            'op': 'add'
                                        });
                                    } else {
                                        if (val_maintag[0].oldValue != val_maintag[0].getValue()) {
                                            // main tag has changed (only new value)
                                            // collect data to 'delete' old main tag
                                            deleteTags.push({
                                                'key': attr_maintag[0].getValue(),
                                                'value': val_maintag[0].oldValue,
                                                'id': me.old_main_tag.get('id'),
                                                'op': 'delete'
                                            });
                                            // collect data to 'add' new main tag
                                            newTags.push({
                                                'key': attr_maintag[0].getValue(),
                                                'value': val_maintag[0].getValue(),
                                                'op': 'add'
                                            });
                                        }
                                    // else: main tag has not changed, do nothing
                                    }
                                }
                            }
							
                            // 'normal' tags
                            var attrs = Ext.ComponentQuery.query('combobox[name=tg_combobox]');
                            var values = Ext.ComponentQuery.query('[name=tg_valuefield]');
                            if (attrs.length > 0 && values.length > 0 && attrs.length == values.length) {
                                for (var i=0; i<attrs.length; i++) {
									
                                    // check for changes
                                    if (!attrs[i].oldAttribute) {
                                        // brand new tag (new key and new value)
                                        // collect data to 'add' new tag
                                        newTags.push({
                                            'key': attrs[i].getValue(),
                                            'value': values[i].getValue(),
                                            'op': 'add'
                                        });
                                    } else {
                                        // tag existed already
                                        if (attrs[i].oldAttribute != attrs[i].getValue()) {
                                            // tag has changed (new key and value)
                                            // collect data to 'add' new tag
                                            newTags.push({
                                                'key': attrs[i].getValue(),
                                                'value': values[i].getValue(),
                                                'op': 'add'
                                            });
                                        } else {
                                            if (values[i].oldValue != values[i].getValue()) {
                                                // tag has changed (only new value)
                                                // try to collect data to 'delete' old tag
                                                for (var i in me.old_tags) {
                                                    if (me.old_tags[i].get('key') == attrs[i].getValue()) {
                                                        var t = me.old_tags.pop(me.old_tags[i]);
                                                        deleteTags.push({
                                                            'key': t.get('key'),
                                                            'value': t.get('value'),
                                                            'id': t.get('id'),
                                                            'op': 'delete'
                                                        });
                                                    }
                                                }
												
                                                // collect data to 'add' new tag
                                                newTags.push({
                                                    'key': attrs[i].getValue(),
                                                    'value': values[i].getValue(),
                                                    'op': 'add'
                                                });
                                            } else {
                                                // tag has not changed
                                                // remove tag from list
                                                me.old_tags.pop(me.old_tags[i]);
                                            }
                                        }
                                    }
                                }
                            }
							
                            // check if there are deleted tags (still in list)
                            for (var i in me.old_tags) {
                                deleteTags.push({
                                    'key': me.old_tags[i].get('key'),
                                    'value': me.old_tags[i].get('value'),
                                    'id': me.old_tags[i].get('id'),
                                    'op': 'delete'
                                });
                            }
							
                            // only do submit if something changed
                            if (newTags.length > 0 || deleteTags.length > 0) {
                                // put together diff object
                                var diffObject = {
                                    'activities': [

                                    {
                                        'id': me.activity_id,
                                        'version': me.version,
                                        'taggroups': [
                                        {
                                            'id': (me.selected_taggroup) ? me.selected_taggroup.get('id') : null,
                                            'op': (me.selected_taggroup) ? null : 'add',
                                            'tags': newTags.concat(deleteTags)
                                        }
                                        ]
                                    }
                                    ]
                                    };
									
                                // send JSON through AJAX request
                                Ext.Ajax.request({
                                    url: '/activities',
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json;charset=utf-8'
                                    },
                                    jsonData: diffObject,
                                    success: function(response, options) {
                                        Ext.Msg.alert('Success', 'The information was successfully submitted. It will be reviewed shortly.');
                                        form.up('window').close();
                                    },
                                    failure: function(response, options) {
                                        Ext.Msg.alert('Failure', 'The information could not be submitted.');
                                        form.up('window').close();
                                    }
                                });
                                console.log(diffObject);
                            } else {
                                Ext.Msg.alert('Notice', 'No changes were made.');
                                form.up('window').close();
                            }
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
                // fill tags into separate arrays
				
                me.selected_taggroup.tags().each(function(record) {
					
                    if (me.selected_taggroup.main_tag().first() && record.get('id') == me.selected_taggroup.main_tag().first().get('id')) {
                        me.old_main_tag = record;
                    } else {
                        me.old_tags.push(record);
                    }
                });

                // first display main tag (if available)
                if (me.old_main_tag) {
                    var fieldContainer = this._getFieldContainer(store, completeStore, true, true, me.old_main_tag.get('key'), me.old_main_tag.get('value'));
                    form.insert(0, fieldContainer);
                }
				
                // then display all 'normal' tags
                for (var t in me.old_tags) {
                    var fieldContainer = this._getFieldContainer(store, completeStore, true, false, me.old_tags[t].get('key'), me.old_tags[t].get('value'));
                    form.insert(1, fieldContainer);
                }
				
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
                        // store old value
                        newField['oldValue'] = initialValue;
                        newField.setValue(initialValue);
                        // 'reset' initialValue
                        initialValue = null;
                    }
                    fieldContainer.insert(1, newField);
                }
            }
        });
        // if initialAttribute was provided (when editing selected TagGroup), then show its value
        if (initialAttribute) {
            // store old value
            cb['oldAttribute'] = initialAttribute;
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
