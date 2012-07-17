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
            'lo_moderatorpendingpanel gridpanel[itemId=activityGrid]': {
                select: this.onPendingActivityGridSelect
            },
            'lo_moderatorpendingpanel gridpanel[itemId=stakeholderGrid]': {
                select: this.onPendingStakeholderGridSelect
            }
        });
    },

    onRender: function(comp){
        this.getPendingActivityGridStore().load();
        this.getPendingStakeholderGridStore().load();
    },
    
    onPendingActivityGridSelect: function(rowmodel, record) {
        
        // Get record
        if (record) {
            var guid = record.get('id');
            var panel = this.getReviewPanel();
            // Use AJAX to get data used to update panel
            Ext.Ajax.request({
                url: '/activities/history/' + guid,
                params: {
                    status: 'active,pending,overwritten'
                },
                success: function(response) {
                    // Update panel with data received
                    panel.updateContentActivity(
                        panel,
                        Ext.JSON.decode(response.responseText)
                    );
                }
            });
        }
    },
    
    onPendingStakeholderGridSelect: function(rowmodel, record) {

        // Get record
        if (record) {
            var guid = record.get('id');
            var panel = this.getReviewPanel();
            // Use AJAX to get data used to update panel
            Ext.Ajax.request({
                url: '/stakeholders/history/' + guid,
                params: {
                    status: 'active,pending,overwritten'
                },
                success: function(response) {
                    // Update panel with data received
                    panel.updateContentStakeholder(
                        panel,
                        Ext.JSON.decode(response.responseText)
                    );
                }
            });
        }
    }
});