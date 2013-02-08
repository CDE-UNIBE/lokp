Ext.define('Lmkp.controller.moderation.Pending', {
    extend: 'Ext.app.Controller',

    stores: [
        'PendingActivityGrid',
        'PendingStakeholderGrid'
    ],

    views: [
        'moderation.CompareReview'
    ],

    stringFunctions: null,

    init: function() {
        // Load the stores
        this.getPendingActivityGridStore().load();
        this.getPendingStakeholderGridStore().load();

        this.stringFunctions = Ext.create('Lmkp.utils.StringFunctions');

        this.control({
            'gridpanel[itemId=pendingActivityGridPanel] templatecolumn[name=compareButtonColumn]': {
                click: this.onCompareButtonClick
            },
            'gridpanel[itemId=pendingStakeholderGridPanel] templatecolumn[name=compareButtonColumn]': {
                click: this.onCompareButtonClick
            },
            'gridcolumn[name=identifierColumn]': {
                afterrender: this.onIdentifierColumnAfterrender
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

            var title = 'Compare versions';
            if (type == 'activities') {
                title += ' of Activity ' + this.stringFunctions._shortenIdentifier(id);
            } else if (type == 'stakeholders') {
                title += ' of Stakeholder ' + this.stringFunctions._shortenIdentifier(id);
            }

            var win = controller._createWindow(title);
            win.show();
            win.setLoading(true);
            win.add({
                xtype: 'lo_moderatorcomparereview',
                action: 'compare'
            });

            controller.reloadCompareTagGroupStore(
                'compare', type, id
            );
        }
    },

    /**
     * Nicely render 'identifier' column of Activity and Stakeholder grid.
     */
    onIdentifierColumnAfterrender: function(comp) {
        var me = this;
        comp.renderer = function(value, metaData, record) {
            if (value) {
                return me.stringFunctions._shortenIdentifier(value);
            } else {
                return Lmkp.ts.msg('gui_unknown');
            }
        }
    }
});