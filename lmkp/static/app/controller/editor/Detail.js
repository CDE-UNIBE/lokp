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
    'Filter'
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
            }
        });
    },

    onShowDetailsToggle: function(button, pressed, eOpts) {
        var taggrouppanels = Ext.ComponentQuery.query('lo_editordetailpanel taggrouppanel');
        for (var i = 0; i < taggrouppanels.length; i++) {
            taggrouppanels[i].toggleDetailButton(pressed);
        }
    },

    onAddTaggroupButtonClick: function(button, event, eOpts){

        var detailPanel = Ext.ComponentQuery.query('lo_editordetailpanel')[0];

        var selection = detailPanel.getCurrent()

        // If no activity is selected, show an info window and exit.
        if(!selection){
            Ext.Msg.show({
                title: 'Edit Activity',
                msg: 'Please select an activity first.',
                buttons: Ext.Msg.OK,
                icon: Ext.window.MessageBox.INFO
            });
            return;
        }

        // create window and pass entire activity (needed because ActivityProtocol needs all old TagGroups as well)
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
