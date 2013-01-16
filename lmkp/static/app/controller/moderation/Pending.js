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

    onCompareButtonClick: function(grid) {
        /**
         * Show an overlay window which allows to compare two versions of an
         * Activity or a Stakeholder
         */

        var record = grid.getSelectionModel().getSelection()[0];

        if (record) {

            // Activity or Stakeholder?
            var type;
            if (record.modelName == 'Lmkp.model.Activity') {
                type = 'activities';
            } else if (record.modelName == 'Lmkp.model.Stakeholder') {
                type = 'stakeholders';
            }

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
                'compare', type, record.get('id')
            );
        }
    }
});