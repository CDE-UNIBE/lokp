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
            /*'lo_editordetailpanel button[itemId=add-activity-button]':{
                click: this.onAddActivityButtonClick
            },*/
            'lo_editordetailpanel button[itemId="show-all-details"]': {
                toggle: this.onShowDetailsToggle
            },
            'lo_editordetailpanel button[name=editTaggroup]': {
                click: this.onEditTaggroupButtonClick
            }
        });
    },

    onEditTaggroupButtonClick: function(button) {
        var taggroup = button.selected_taggroup;
        if (taggroup) {
            var activity = taggroup.getActivity();
            if (activity) {
                var win = Ext.create('Lmkp.view.activities.NewTaggroupWindow', {
                    activity_id: activity.get('id'),
                    version: activity.get('version'),
                    selected_taggroup: taggroup
                });
                win.show();
            }
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

        // create window
        var win = Ext.create('Lmkp.view.activities.NewTaggroupWindow', {
            activity_id: selection.get('id'),
            version: selection.get('version'),
            selected_taggroup: null
        });
        win.show();
    },

    onAddActivityButtonClick: function(button, event, eOpts){
        /**
    	// Open new window with form to add new activity.
    	// The form fields are requested before creating the window.
    	// This allows to create a nicely centered form window.
    	Ext.Ajax.request({
    		url: '/config/form/activities',
    		success: function(response) {
    			var formConfig = Ext.decode(response.responseText);
    			var win = Ext.create('Lmkp.view.activities.NewActivityWindow', {
    				config: formConfig
    			});
    			win.show();
    		}
    	});
    	*/
    	
        // var mandatoryStore = Ext.create('Lmkp.store.ActivityConfig');
        // mandatoryStore.filter("allowBlank", false);
        // mandatoryStore.load();
    	
        var win = Ext.create('Lmkp.view.activities.NewActivityWindow');
        win.show();
    }

});
