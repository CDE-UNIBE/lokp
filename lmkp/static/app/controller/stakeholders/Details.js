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
            }
        });
    },

    onHistoryPanelSelect: function(rowModel, record, index, eOpts){
        this.getStakeholderDetailWindow()._populateDetails(record);
    },

    onCloseWindowButtonClick: function(){
        this.getStakeholderDetailWindow().close();
    }
    
    
});