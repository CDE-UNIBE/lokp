Ext.define('Lmkp.controller.activities.Details', {
    extend: 'Ext.app.Controller',

    refs: [{
        ref: 'activityDetailWindow',
        selector: 'lo_activitydetailwindow'
    }],

    init: function() {
        this.control({
            'lo_activitydetailwindow gridpanel[itemId="historyPanel"]': {
                select: this.onHistoryPanelSelect
            },
            'lo_activitydetailwindow button[itemId="closeWindowButton"]': {
                click: this.onCloseWindowButtonClick
            },
            'lo_activitydetailwindow button[name=editTaggroup]': {
                click: this.onEditTaggroupButtonClick
            }
        });
    },

    onHistoryPanelSelect: function(rowModel, record, index, eOpts){
        this.getActivityDetailWindow()._populateDetails(record, record.get('status') == 'pending');
    },

    onCloseWindowButtonClick: function(){
        this.getActivityDetailWindow().close();
    },

    /**
     * If any Tag Group is to be edited, show same window as when adding a new
     * Activity but fill out the form with the current values.
     */
    onEditTaggroupButtonClick: function(button) {
        var activityPanel = button.up('lo_activitypanel');
        if (activityPanel && activityPanel.contentItem) {
            var newActivityController = this.getController('activities.NewActivity');
            newActivityController.showNewActivityWindow(
                // Provide current item
                activityPanel.contentItem
            );
        }
    }

});