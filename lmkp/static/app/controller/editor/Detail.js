Ext.define('Lmkp.controller.editor.Detail', {
    extend: 'Ext.app.Controller',

    models: [
    'Config'
    //'ActivityGrid'
    ],
    requires: ['Ext.window.MessageBox'],
    stores: ['Config', 'ActivityGrid'],

    views: ['Filter'],

    init: function() {
        this.control({
            'lo_editordetailpanel button[itemId=add-taggroup-button]':{
                click: this.onAddTaggroupButtonClick
            },
            'lo_editordetailpanel button[itemId=add-activity-button]':{
                click: this.onAddActivityButtonClick
            }
        });
    },

    onAddTaggroupButtonClick: function(button, event, eOpts){
        // Get the selected item in the grid panel
        var gridPanel = Ext.ComponentQuery.query('lo_editortablepanel gridpanel[itemId=activityGrid]')[0];

        var selection = gridPanel.getSelectionModel().getSelection()[0];

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
    		url: '/config/form',
    		success: function(response) {
    			var formConfig = Ext.decode(response.responseText);
    			var win = Ext.create('Lmkp.view.activities.NewActivityWindow', {
    				config: formConfig
    			});
    			win.show();
    		}
    	});
    	*/
    	
    	// var mandatoryStore = Ext.create('Lmkp.store.Config');
    	// mandatoryStore.filter("allowBlank", false);
    	// mandatoryStore.load();
    	
    	var win = Ext.create('Lmkp.view.activities.NewActivityWindow');
    	win.show();
    	
    	
    }

});
