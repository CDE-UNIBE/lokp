Ext.define('Lmkp.controller.EditFilter', {
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
            'filterPanel panel[id=detailPanel] button[id=add-taggroup-button]':{
                click: this.onAddTaggroupButtonClick
            },
            'filterPanel panel[id=detailPanel] button[id=add-activity-button]':{
                click: this.onAddActivityButtonClick
            }
        });
    },

    onAddTaggroupButtonClick: function(button, event, eOpts){
        // Get the selected item in the grid panel
        var gridPanel = Ext.ComponentQuery.query('filterPanel gridpanel[id=filterResults]')[0];
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
        
        console.log(selection);
        console.log(selection.taggroups());

		// create window and pass entire activity (needed because ActivityProtocol needs all old TagGroups as well)
    	var win = Ext.create('Lmkp.view.activities.NewTaggroupWindow', {
    		activity: selection,
    		selected_taggroup: null
    	});
    	win.show();
    },

    onAddActivityButtonClick: function(button, event, eOpts){
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
    }

});
