Ext.define('Lmkp.controller.editor.Detail', {
    extend: 'Ext.app.Controller',

    models: [
    'Config'
    ],

    requires: [
    'Ext.window.MessageBox'
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
            'lo_editordetailpanel button[itemId=add-taggroup-button]':{
                click: this.onAddTaggroupButtonClick
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
            }
        });
    },

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
    }
});
