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
                select: this.onPendingGridSelect
            },
            'lo_moderatorpendingpanel gridpanel[itemId=stakeholderGrid]': {
                select: this.onPendingGridSelect
            },
            'lo_moderatorreviewpanel checkbox[name=comment_checkbox]': {
                change: this.onReviewCommentCheckboxChange
            },
            'lo_moderatorreviewpanel button[name=review_submit]': {
                click: this.onReviewSubmitButtonClick
            },
            'gridpanel gridcolumn[name=completeColumn]': {
                afterrender: this.renderCompleteColumn
            }
        });
    },

    onRender: function(comp){
        this.getPendingActivityGridStore().load();
        this.getPendingStakeholderGridStore().load();
    },

    renderCompleteColumn: function(comp) {
        comp.renderer = function(value) {
            if (value == true) {
                return 'OK'
            } else {
                return '-'
            }
        }
    },
    
    onPendingGridSelect: function(rowmodel, record) {

        // Activity or Stakeholder?
        var type = null;
        if (rowmodel.getStore().storeId == 'PendingActivityGrid') {
            type = 'activities';
        } else if (rowmodel.getStore().storeId == 'PendingStakeholderGrid') {
            type = 'stakeholders';
        }
        
        // Get record
        if (record && type) {
            var guid = record.get('id');
            var panel = this.getReviewPanel();
            // Use AJAX to get data used to update panel
            Ext.Ajax.request({
                url: '/' + type + '/history/' + guid,
                params: {
                    status: 'active,pending,overwritten',
                    involvements: 'full',
                    mark_complete: 'true'
                },
                method: 'GET',
                success: function(response) {
                    // Update panel with data received
                    panel.updateContent(
                        Ext.JSON.decode(response.responseText),
                        type
                    );
                }
            });
        }
    },

    /**
     * Toggle the visibility of the textarea to add comments to review decision.
     */
    onReviewCommentCheckboxChange: function(checkbox, newValue) {
        var textarea = checkbox.up('form').query(
            'textarea[name=comment_textarea]'
        )[0];
        if (textarea) {
            textarea.setVisible(newValue);
        }
    },

    /**
     * Send a review request
     */
    onReviewSubmitButtonClick: function(button) {
        var form = button.up('form').getForm();
        var reviewPanel = this.getReviewPanel();
        var activityStore = this.getPendingActivityGridStore();
        var stakeholderStore = this.getPendingStakeholderGridStore();
        if (form.isValid()) {
            form.submit({
                success: function(form, action) {
                    // Reload pending store
                    if (button.store_type == 'activities') {
                        activityStore.load();
                    } else if (button.store_type == 'stakeholders') {
                        stakeholderStore.load();
                    }
                    // Update panel
                    reviewPanel.showInitialContent();
                    // Give feedback
                    Ext.Msg.alert('Success', action.result.msg);
                },
                failure: function(form, action) {
                    // Give feedback
                    Ext.Msg.alert('Failure', action.result.msg);
                }
            });
        }
    }
});