Ext.define('Lmkp.controller.moderation.Pending', {
    extend: 'Ext.app.Controller',

    stores: [
        'PendingActivityGrid',
        'PendingStakeholderGrid'
    ],

    views: [
        'moderation.CompareReview'
    ],

    init: function() {
        // Load the stores
        this.getPendingActivityGridStore().load();
        this.getPendingStakeholderGridStore().load();

        this.control({
            'gridpanel[itemId=pendingActivityGridPanel] templatecolumn[name=compareButtonColumn]': {
                click: this.onCompareButtonClick
            },
            'gridpanel[itemId=pendingStakeholderGridPanel] templatecolumn[name=compareButtonColumn]': {
                click: this.onCompareButtonClick
            }
        });
    },

    onCompareButtonClick: function(item) {
        /**
         * Show an overlay window which allows to compare two versions of an
         * Activity or a Stakeholder
         * Item is either a gridview item (when selecting an item on the grid)
         * or a self constructed item (when loading directly a compare view).
         * The latter must contain an 'id' (guid) and a 'type'
         * (activities/stakeholders).
         */

        var id, type;

        if (item && item.xtype && item.xtype == 'gridview') {
            var record = item.getSelectionModel().getSelection()[0];
            if (record) {
                id = record.get('id');
                // Activity or Stakeholder?
                if (record.modelName == 'Lmkp.model.Activity') {
                    type = 'activities';
                } else if (record.modelName == 'Lmkp.model.Stakeholder') {
                    type = 'stakeholders';
                }
            }
        } else if (item && item.type && item.identifier) {
            id = item.identifier;
            type = item.type;
        }

        if (id && type) {
            var controller = this.application.getController('moderation.CompareReview');

            var win = controller._createWindow();
            win.show();
            win.setLoading(true);
            win.setTitle('Compare');
            win.add({
                xtype: 'lo_moderatorcomparereview',
                action: 'compare'
            });

            controller.reloadCompareTagGroupStore(
                'compare', type, id
            );
        }
    }
});