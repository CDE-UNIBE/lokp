Ext.define('Lmkp.controller.activities.Details', {
    extend: 'Ext.app.Controller',

    refs: [{
        ref: 'activityDetailWindow',
        selector: 'lo_activitydetailwindow'
    }],

    init: function() {
        this.control({
            'lo_activitydetailwindow gridpanel[itemId="historyPanel"]': {
                render: this.onHistoryPanelRender,
                select: this.onHistoryPanelSelect
            },
            'lo_activitydetailwindow button[itemId="closeWindowButton"]': {
                click: this.onCloseWindowButtonClick
            }
        });
    },

    onHistoryPanelRender: function(comp){

    },

    onHistoryPanelSelect: function(rowModel, record, index, eOpts){
        this.getActivityDetailWindow()._populateDetails(record);
    },

    onCloseWindowButtonClick: function(){
        this.getActivityDetailWindow().close();
    }


});