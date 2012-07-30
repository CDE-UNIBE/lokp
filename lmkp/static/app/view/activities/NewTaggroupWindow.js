Ext.define('Lmkp.view.activities.NewTaggroupWindow', {
    extend: 'Ext.window.Window',
    alias: ['widget.lo_newtaggroupwindow'],

    requires: ['Lmkp.view.activities.NewTaggroupPanel'],
	
    layout: 'fit',
    defaults: {
        border: 0
    },
    width: 400,
	
    // needed to keep track of original tags
    old_tags: [],
    old_main_tag: null,

    config: {
        cb_tag: 'tg_combobox_tag',
        cb_maintag: 'tg_combobox_maintag'
    },

    items: [
        {
            xtype: 'panel',
            bodyPadding: 5,
            html: 'Loading ...'
        }
    ],
	
    initComponent: function() {
		
        var me = this;
        // 'reset' original tracks
        me.old_tags = [];
        me.old_main_tag = null;

        // set window title
        var action = (me.selected_taggroup) ? 'Change' : 'Add';
        this.title = action + ' information';
		
        if (me.item_identifier && me.version && me.item_type) {

            // Activity or Stakeholder?
            var url = null;
            var diff_root = null;
            var configStore = null;
            if (me.item_type == 'activity') {
                url = '/activities';
                diff_root = 'activities';
                configStore = 'Lmkp.store.ActivityConfig';
            } else if (me.item_type == 'stakeholder') {
                url = '/stakeholders';
                diff_root = 'stakeholders';
                configStore = 'Lmkp.store.StakeholderConfig';
            }

            // prepare the form
            var form = Ext.create('Ext.form.Panel', {
                border: 0,
                bodyPadding: 5,
                layout: 'anchor',
                defaults: {
                    anchor: '100%'
                },
                items: [{
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
                            var main_tag = form.query('lo_newtaggrouppanel').length == 0;
                            form.insert(form.items.length-1, {
                                xtype: 'lo_newtaggrouppanel',
                                is_maintag: main_tag,
                                removable: true,
                                main_store: store,
                                complete_store: completeStore
                            });
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

                            // Prepare values
                            var main_tag = new Object();
                            var newTags = [];
                            var deleteTags = [];
                            // Old tags (there on initial load of window)
                            var ot = me.old_tags;
                            ot.push(me.old_main_tag)

                            // Go through each tag group panel
                            var tgpanels = form.query('lo_newtaggrouppanel');
                            for (var i=0; i<tgpanels.length; i++) {
                                var c = tgpanels[i]
                                if (c.getInitialValue() == c.getValueValue()
                                    && c.getInitialKey() == c.getKeyValue()) {
                                    // Tag has not changed, remove it from list
                                    // Delete old tag from list
                                    for (var x in ot) {
                                        if (ot[x].get('id') == c.getInitialTagId()) {
                                            ot.splice(x, 1);
                                        }
                                    }
                                } else {
                                    // Tag has changed
                                    newTags.push({
                                        'key': c.getKeyValue(),
                                        'value': c.getValueValue(),
                                        'op': 'add'
                                    });
                                    // Only add to 'deleted' if it had an ID
                                    if (c.getInitialTagId()) {
                                        deleteTags.push({
                                            'key': c.getInitialKey(),
                                            'value': c.getInitialValue(),
                                            'id': c.getInitialTagId(),
                                            'op': 'delete'
                                        });
                                    }
                                    // Delete old tag from list
                                    for (var x in ot) {
                                        if (ot[x].get('id') == c.getInitialTagId()) {
                                            ot.splice(x, 1);
                                        }
                                    }
                                }
                                if (c.isMainTag()) {
                                    main_tag.key = c.getKeyValue();
                                    main_tag.value = c.getValueValue();
                                }
                            }
                            // Check if main tag has changed
                            var new_main_tag = null;
                            if (me.old_main_tag.get('key') != main_tag.key
                                || me.old_main_tag.get('value') != main_tag.value) {
                                new_main_tag = {
                                    'key': main_tag.key,
                                    'value': main_tag.value
                                };
                            }

                            // Any remaining tag has been deleted
                            for (x in ot) {
                                deleteTags.push({
                                    'key': ot[x].get('key'),
                                    'value': ot[x].get('value'),
                                    'id': ot[x].get('id'),
                                    'op': 'delete'
                                });
                            }

                            // only do submit if something changed
                            if (newTags.length > 0 || deleteTags.length > 0) {
                                // put together diff object
                                var taggroup = {
                                    'id': (me.selected_taggroup) ? me.selected_taggroup.get('id') : null,
                                    'op': (me.selected_taggroup) ? null : 'add',
                                    'tags': newTags.concat(deleteTags)
                                };
                                if (new_main_tag) {
                                    taggroup['main_tag'] = new_main_tag;
                                }
                                var diffObject = {}
                                diffObject[diff_root] = [{
                                    'id': me.item_identifier,
                                    'version': me.version,
                                    'taggroups': [taggroup]
                                }];
									
                                // send JSON through AJAX request
                                Ext.Ajax.request({
                                    url: url,
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json;charset=utf-8'
                                    },
                                    jsonData: diffObject,
                                    success: function(response, options) {
                                        Ext.Msg.alert('Success', 'The information was successfully submitted. It will be reviewed shortly.');
                                        // Fire event to reload detail panel
                                        form.up('window').fireEvent('successfulEdit');
                                        form.up('window').close();
                                    },
                                    failure: function(response, options) {
                                        Ext.Msg.alert('Failure', 'The information could not be submitted.');
                                        form.up('window').close();
                                    }
                                });
                            } else {
                                Ext.Msg.alert('Notice', 'No changes were made.');
                                form.up('window').close();
                            }
                        }
                    }
                }]
            });
			
            // load the config store
            var store = Ext.create(configStore);
            var completeStore = Ext.create(configStore);
            store.load(function() {
                // another instance of the config store is needed to keep track
                // of all attributes available
                completeStore.load(function() {
                    // Only continue both stores are loaded

                    if (me.selected_taggroup) {
                        var profile_info = null;

                        // Keep track of tags
                        me.selected_taggroup.tags().each(function(record) {
                            // Only keep track of attributes available in
                            // configuration store
                            if (store.find('fieldLabel', record.get('key')) != -1) {
                                // Treat main tags and 'normal' tags differently
                                if (me.selected_taggroup.main_tag().first() &&
                                    record.get('id') == me.selected_taggroup.main_tag().first().get('id')) {
                                    me.old_main_tag = record;
                                } else {
                                    me.old_tags.push(record);
                                }
                            } else {
                                // Show a message that at least one attribute is
                                // not shown because of profile
                                profile_info = true;
                            }
                        });

                        // Display main tag first (if available)
                        if (me.old_main_tag) {
                            form.insert(0, {
                                xtype: 'lo_newtaggrouppanel',
                                is_maintag: true,
                                removable: true,
                                main_store: store,
                                complete_store: completeStore,
                                initial_key: me.old_main_tag.get('key'),
                                initial_value: me.old_main_tag.get('value'),
                                initial_tagid: me.old_main_tag.get('id')
                            });
                        }

                        // Display all 'normal' tags
                        for (var t in me.old_tags) {
                            form.insert(1, {
                                xtype: 'lo_newtaggrouppanel',
                                is_maintag: false,
                                removable: true,
                                main_store: store,
                                complete_store: completeStore,
                                initial_key: me.old_tags[t].get('key'),
                                initial_value: me.old_tags[t].get('value'),
                                initial_tagid: me.old_tags[t].get('id')
                            });
                        }
                    } else {
                        // If no TagGroup was selected to edit, show initial
                        // attribute selection
                        form.insert(0, {
                            xtype: 'lo_newtaggrouppanel',
                            is_maintag: true,
                            removable: false,
                            main_store: store,
                            complete_store: completeStore
                        });
                    }

                    // Show information if some attributes were skipped because
                    // of profile
                    if (profile_info) {
                        form.insert(0, {
                            xtype: 'panel',
                            html: 'Some of the attributes cannot be edited '
                                + 'because they are not part of the currently selected '
                                + 'profile.',
                            bodyCls: 'notice',
                            bodyPadding: 5,
                            margin: '0 0 5 0'
                        });
                    }

                    // Remove the loading panel before showing form
                    me.removeAll();
                    me.add(form);
                });
            });
        }
        this.callParent(arguments);
    }
});
