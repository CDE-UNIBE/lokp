Ext.define('Lmkp.controller.moderator.Pending', {
    extend: 'Ext.app.Controller',

    stores: [
        'PendingActivityGrid',
        'PendingStakeholderGrid'
    ],
    
    refs: [
        {
            ref: 'reviewPanel',
            selector: 'lo_moderatorreviewpanel'
        }
    ],

    init: function(){
        this.control({
            'lo_moderatorpendingpanel': {
                render: this.onRender
            },
            'gridpanel[itemId=activityGrid]': {
                select: this.onPendingActivityGridSelect
            },
            'gridpanel[itemId=pendingStakeholderGrid]': {
                select: this.onPendingStakeholderGridSelect
            }
        });
    },

    onRender: function(comp){
        this.getPendingActivityGridStore().load();
        this.getPendingStakeholderGridStore().load();
    },
    
    onPendingActivityGridSelect: function(rowmodel, record) {
        
        // get record
        if (record) {
            var guid = record.get('id');
        }
        
        var panel = this.getReviewPanel();
        console.log(panel);
        
        console.log("coming soon");
    },
    
    onPendingStakeholderGridSelect: function(rowmodel, record) {
        console.log("coming soon");
        console.log(record);
    }
});