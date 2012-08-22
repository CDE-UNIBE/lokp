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
        }, {
            ref: 'activityGridPanel',
            selector: 'lo_moderatorpendingpanel gridpanel[itemId=activityGrid]'
        }, {
            ref: 'stakeholderGridPanel',
            selector: 'lo_moderatorpendingpanel gridpanel[itemId=stakeholderGrid]'
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
            'lo_moderatorreviewpanel button[name=editTaggroup]': {
                click: this.onEditTaggroupButtonClick
            },
            'lo_moderatorreviewpanel button[name=review_submit]': {
                click: this.onReviewSubmitButtonClick
            },
            'gridpanel gridcolumn[name=completeColumn]': {
                afterrender: this.renderCompleteColumn
            }
        });
    },

    /**
     * This is based very much on the function with the same name in
     * controller\editor\Detail.js
     * However, after successfully editing a taggroup, function
     * 'onPendingEdit' is called to reload the content.
     */
    onEditTaggroupButtonClick: function(button) {

        var taggroup = button.selected_taggroup;

        // Activity or Stakeholder?
        var taggrouppanel = button.up('panel');
        var panel = taggrouppanel ? taggrouppanel.up('panel') : null;

        var item_type = null;
        var item = null;
        if (panel && taggroup) {
            if (panel.getXType() == 'lo_activitypanel') {
                item_type = 'activity';
                item = taggroup.getActivity();
            } else if (panel.getXType() == 'lo_stakeholderpanel') {
                item_type = 'stakeholder';
                item = taggroup.getStakeholder();
            }
        }

        if (item_type) {
            // Prepare the window
            var win = Ext.create('Lmkp.view.activities.NewTaggroupWindow', {
                item_identifier: item.get('id'),
                version: item.get('version'),
                selected_taggroup: taggroup,
                item_type: item_type
            });

            // When inserted successfully, call function to reload content
            var controller = this;
            win.on('successfulEdit', function() {
                controller.onPendingEdit(item, button);
            });
            // Show
            win.show();
        }
    },

    onRender: function(comp){
        this.getPendingActivityGridStore().load();
        this.getPendingStakeholderGridStore().load();
    },

    renderCompleteColumn: function(comp) {
        comp.renderer = function(value) {
            if (value.length == 0) {
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
                    status: 'pending,active,inactive,deleted,rejected,edited',
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
    },

    /**
     * Simulate a review decision and reload content
     */
    onPendingEdit: function(item, button) {

        // Activity or Stakeholder?
        var item_type = null;
        if (item.modelName == 'Lmkp.model.Activity') {
            item_type = 'activities';
        } else if (item.modelName == 'Lmkp.model.Stakeholder') {
            item_type = 'stakeholders';
        }

        if (item_type) {
            var activityStore = this.getPendingActivityGridStore();
            var activityGridPanel = this.getActivityGridPanel();
            var stakeholderStore = this.getPendingStakeholderGridStore();
            var stakeholderGridPanel = this.getStakeholderGridPanel();

            // Do an AJAX request to simulate the submission of a review
            Ext.Ajax.request({
                url: item_type + '/review',
                method: 'POST',
                params: {
                    'review_decision': 3, // 'edited'
                    'identifier': item.get('id'),
                    'version': item.get('version')
                },
                success: function() {

                    // Activity or Stakeholder?
                    var store = null;
                    var gridpanel = null;
                    if (item_type == 'activities') {
                        store = activityStore;
                        gridpanel = activityGridPanel;
                    } else if (item_type == 'stakeholders') {
                        store = stakeholderStore;
                        gridpanel = stakeholderGridPanel;
                    }
                    
                    if (store && gridpanel) {
                        // Reload store
                        store.load(function() {
                            // After reload, select record in grid to show its details
                            var record = this.findRecord('id', item.get('id'));
                            gridpanel.getSelectionModel().select([record]);
                            // Give feedback
                            Ext.Msg.alert('Success', 'Edited changes were submitted');
                        });
                    }
                },
                failure: function() {
                    // Give feedback
                    Ext.Msg.alert('Failure', 'Edited changes could not be submitted');
                }
            });
        }
    }
});