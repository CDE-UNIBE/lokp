Ext.define('Lmkp.controller.stakeholders.Details', {
    extend: 'Ext.app.Controller',

    refs: [{
        ref: 'stakeholderDetailWindow',
        selector: 'lo_stakeholderdetailwindow'
    }],

    init: function() {
        this.control({
            'lo_stakeholderdetailwindow gridpanel[itemId="historyPanel"]': {
                select: this.onHistoryPanelSelect
            },
            'lo_stakeholderdetailwindow button[itemId="closeWindowButton"]': {
                click: this.onCloseWindowButtonClick
            },
            'lo_stakeholderdetailwindow button[name=editTaggroup]': {
                click: this.onEditTaggroupButtonClick
            }
        });
    },

    onHistoryPanelSelect: function(rowModel, record, index, eOpts){
        this.getStakeholderDetailWindow()._populateDetails(record);
    },

    onCloseWindowButtonClick: function(){
        this.getStakeholderDetailWindow().close();
    },

    onEditTaggroupButtonClick: function(button) {
        var stakeholderPanel = button.up('lo_stakeholderpanel');
        if (stakeholderPanel && stakeholderPanel.contentItem) {
            var newActivityController =
                this.getController('activities.NewActivity');
            newActivityController.showNewStakeholderWindow(
                // Provide current item
                stakeholderPanel.contentItem
            );
        }
    }
    
    
});