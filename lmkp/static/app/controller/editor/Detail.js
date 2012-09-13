Ext.define('Lmkp.controller.editor.Detail', {
    extend: 'Ext.app.Controller',

    models: [
    'Config'
    ],

    requires: [
        'Ext.window.MessageBox',
        'Lmkp.utils.MessageBox'
    ],

    stores: [
    'ActivityConfig',
    'ActivityGrid'
    ],

    views: [
    'activities.Details',
    'activities.Filter'
    ],

    init: function() {
        this.control({
            /*
            'lo_editordetailpanel button[itemId=add-taggroup-button]':{
                click: this.onAddTaggroupButtonClick
            },
            'lo_editordetailpanel button[itemId=add-involvement-button]': {
                click: this.onAddInvolvementButtonClick
            },
            'lo_editordetailpanel button[itemId=delete-item-button]': {
                click: this.onItemDeleteButtonClick
            },
            'lo_editordetailpanel button[itemId="show-all-details"]': {
                toggle: this.onShowDetailsToggle
            },
            'lo_editordetailpanel button[name=editTaggroup]': {
                click: this.onEditTaggroupButtonClick
            },
            'lo_editordetailpanel lo_activityhistorypanel': {
                activate: this.onHistoryTabActivate
            },
            'lo_editordetailpanel lo_newactivitypanel': {
                activate: this.onNewActivityTabActivate
            },
            'lo_editordetailpanel button[name=deleteInvolvementButton]': {
                click: this.onInvolvementDeleteButtonClick
            }
            */
        });
    },

    /*
    onNewActivityTabActivate: function(panel) {
        // Create and load a store with all mandatory keys
        var mandatoryStore = Ext.create('Lmkp.store.ActivityConfig');
        mandatoryStore.filter('allowBlank', false);
        mandatoryStore.load(function() {
            // Create and load a second store with all keys
            var completeStore = Ext.create('Lmkp.store.ActivityConfig');
            completeStore.load(function() {
                // When loaded, show panel
                panel.showForm(mandatoryStore, completeStore);
            });
        });
    },

    onHistoryTabActivate: function(panel) {
        // Use detailpanel to find currently selected item
        var detailPanel = Ext.ComponentQuery.query('lo_editordetailpanel')[0];
        if (detailPanel) {
            var selected = detailPanel.getCurrent();
        }
        // Activity or Stakeholder?
        var types = null;
        if (selected && selected.modelName) {
            if (selected.modelName == 'Lmkp.model.Activity') {
                types = 'activities';
            } else if (selected.modelName == 'Lmkp.model.Stakeholder') {
                types = 'stakeholders';
            }
        }
        // Use AJAX to get data used to update panel
        if (selected && types) {
            panel.removeAll();
            Ext.Ajax.request({
                url: '/' + types + '/history/' + selected.get('id'),
                params: {
                    involvements: 'full'
                },
                method: 'GET',
                success: function(response) {
                    // Update panel
                    panel.updateContent(
                        Ext.JSON.decode(response.responseText),
                        types
                    );
                }
            });
        }
    },

    onEditTaggroupButtonClick: function(button) {

        var taggroup = button.selected_taggroup;

        // Activity or Stakeholder?
        var taggrouppanel = button.up('panel');
        var panel = taggrouppanel ? taggrouppanel.up('panel') : null;

        var item_type = null;
        var item = null;
        if (panel && taggroup) {
            if (panel.getXType() == 'lo_activitypanel') {
                item_type = 'activity';
                item = taggroup.getActivity();
            } else if (panel.getXType() == 'lo_stakeholderpanel') {
                item_type = 'stakeholder';
                item = taggroup.getStakeholder();
            }
        }

        if (item_type) {
            // Prepare the window
            var win = Ext.create('Lmkp.view.activities.NewTaggroupWindow', {
                item_identifier: item.get('id'),
                version: item.get('version'),
                selected_taggroup: taggroup,
                item_type: item_type
            });
            // When inserted successfully, reload details in panel
            var me = this;
            win.on('successfulEdit', function() {
                var controller = me.getController('editor.Overview');
                controller.showDetails(null, [item]);
            });
            // Show
            win.show();
        }
    },

    onShowDetailsToggle: function(button, pressed) {
        var activityPanel = Ext.ComponentQuery.query('lo_editordetailpanel lo_activitypanel')[0];
        if (activityPanel) {
            var taggroupPanels = activityPanel._getTaggroupPanels();
            for (var i in taggroupPanels) {
                // Toggle the button instead of directly toggling panel
                taggroupPanels[i]._toggleDetailButton(pressed);
            }
        }
    },

    onAddInvolvementButtonClick: function() {
        var detailPanel = Ext.ComponentQuery.query('lo_editordetailpanel')[0];

        var activity = detailPanel.getCurrent()

        // If no activity is selected, show an info window and exit.
        if(!activity.id){
            Ext.Msg.show({
                title: 'Edit Activity',
                msg: 'Please select an activity first.',
                buttons: Ext.Msg.OK,
                icon: Ext.window.MessageBox.INFO
            });
            return;
        }

        var sel = Ext.create('Lmkp.view.stakeholders.StakeholderSelection');

        var me = this;
        sel.on('close', function(panel) {
            var stakeholder = panel.getSelectedStakeholder();
            if (stakeholder) {
                var confirmwindow = Ext.create('Lmkp.utils.MessageBox');
                confirmwindow.confirm('Add Involvement', 'Are you sure?',
                    function(btn) {
                    if (btn === 'yes') {
                        var diffObject = {
                            'activities': [
                                {
                                    'id': activity.get('id'),
                                    'version': activity.get('version'),
                                    'stakeholders': [
                                        {
                                            'op': 'add',
                                            'id': stakeholder.get('id'),
                                            'version': stakeholder.get('version'),
                                            // So far, this is HARD CODED: New
                                            // involvements always have
                                            // Stakeholder_Role 6 (Investor)
                                            'role': 6
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
                            success: function() {
                                // Reload detail panel
                                var controller = me.getController('editor.Overview');
                                controller.showDetails(null, [activity]);
                                // Show feedback
                                Ext.Msg.alert('Success', 'The information was successfully submitted. It will be reviewed shortly.');
                            },
                            failure: function() {
                                Ext.Msg.alert('Failure', 'The information could not be submitted.');
                            }
                        });
                    }
                });
            }
        });
        sel.show();
    },


    onAddTaggroupButtonClick: function(button, event, eOpts){

        var detailPanel = Ext.ComponentQuery.query('lo_editordetailpanel')[0];

        var selection = detailPanel.getCurrent()

        // If no activity is selected, show an info window and exit.
        if(!selection.id){
            Ext.Msg.show({
                title: 'Edit Activity',
                msg: 'Please select an activity first.',
                buttons: Ext.Msg.OK,
                icon: Ext.window.MessageBox.INFO
            });
            return;
        }

        // Activity or Stakeholder?
        var item_type = null;
        if (selection.modelName == 'Lmkp.model.Activity') {
            item_type = 'activity';
        } else if (selection.modelName == 'Lmkp.model.Stakeholder') {
            item_type = 'stakeholder';
        }

        // Prepare the window
        var win = Ext.create('Lmkp.view.activities.NewTaggroupWindow', {
            item_identifier: selection.get('id'),
            version: selection.get('version'),
            selected_taggroup: null,
            item_type: item_type
        });
        // When inserted successfully, reload details in panel
        var me = this;
        win.on('successfulEdit', function() {
            var controller = me.getController('editor.Overview');
            controller.showDetails(null, [selection]);
        });
        win.show();
    },

    onInvolvementDeleteButtonClick: function(button) {

        var confirmwindow = Ext.create('Lmkp.utils.MessageBox');

        var me = this;
        confirmwindow.confirm('Delete', 'Are you sure?', function(btn) {
            if (btn === 'yes') {

                var involvement = (button.up('lo_involvementpanel'))
                    ? button.up('lo_involvementpanel').involvement : null;

                if (involvement) {
                    // Get Activity
                    var activity = involvement.getActivity();

                    // In order to find out Stakeholder, it is necessary to create a
                    // model instance (simulate a store) using the raw data of the
                    // involvement
                    var shStore = Ext.create('Ext.data.Store', {
                        model: 'Lmkp.model.Stakeholder',
                        data: involvement.raw.data,
                        proxy: {
                            type: 'memory',
                            reader: {
                                type: 'json'
                            }
                        }
                    });
                    shStore.load();
                    var stakeholder = shStore.getAt(0);

                    if (activity && stakeholder) {
                        var diffObject = {
                            'activities': [
                                {
                                    'id': activity.get('id'),
                                    'version': activity.get('version'),
                                    'stakeholders': [
                                        {
                                            'op': 'delete',
                                            'id': stakeholder.get('id'),
                                            'version': stakeholder.get('version'),
                                            'role': involvement.get('role_id')
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
                            success: function() {
                                // Reload detail panel
                                var controller = me.getController('editor.Overview');
                                controller.showDetails(null, [activity]);
                                // Show feedback
                                Ext.Msg.alert('Success', 'The information was successfully submitted. It will be reviewed shortly.');
                            },
                            failure: function() {
                                Ext.Msg.alert('Failure', 'The information could not be submitted.');
                            }
                        });
                    }
                }
            }
        });
    },

    onItemDeleteButtonClick: function() {

        var detailPanel = Ext.ComponentQuery.query('lo_editordetailpanel')[0];

        var selection = detailPanel.getCurrent()

        // If no activity is selected, show an info window and exit.
        if(!selection.id){
            Ext.Msg.show({
                title: 'Edit Activity',
                msg: 'Please select an activity first.',
                buttons: Ext.Msg.OK,
                icon: Ext.window.MessageBox.INFO
            });
            return;
        }

        // Activity or Stakeholder?
        var item = null;
        if (selection.modelName == 'Lmkp.model.Activity') {
            item = 'activities';
        } else if (selection.modelName == 'Lmkp.model.Stakeholder') {
            item = 'stakeholders';
        }

        var confirmwindow = Ext.create('Lmkp.utils.MessageBox');

        var me = this;
        confirmwindow.confirm('Delete', 'Are you sure?', function(button) {
            if (button === 'yes') {
                // Collect data: Taggroups
                var deletedTaggroups = [];
                var tgStore = selection.taggroups();
                tgStore.each(function(taggroup) {
                    // Collect data: Tags
                    var deletedTags = [];
                    var tags = taggroup.tags();
                    tags.each(function(tag) {
                        deletedTags.push({
                            'op': 'delete',
                            'id': tag.get('id'),
                            'key': tag.get('key'),
                            'value': tag.get('value')
                        });
                    });
                    deletedTaggroups.push({
                        'op': 'delete',
                        'id': taggroup.get('id'),
                        'tags': deletedTags
                    });
                });

                // Prepare diff
                var diffObject = {};
                diffObject[item] = [
                    {
                        'id': selection.get('id'),
                        'version': selection.get('version'),
                        'taggroups': deletedTaggroups
                    }
                ];

                // send JSON through AJAX
                Ext.Ajax.request({
                    url: item,
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json;charset=utf-8'
                    },
                    jsonData: diffObject,
                    success: function() {
                        // Reload detail panel
                        var controller = me.getController('editor.Overview');
                        controller.showDetails(null, [selection]);
                        // Show feedback
                        Ext.Msg.alert('Success', 'The information was successfully submitted. It will be reviewed shortly.');
                    },
                    failure: function() {
                        Ext.Msg.alert('Failure', 'The information could not be submitted.');
                    }
                });
            }
        });
    }

    */
});
