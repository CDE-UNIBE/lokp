Ext.define('Lmkp.view.items.PendingUserChanges', {
    extend: 'Ext.panel.Panel',
    alias: ['widget.lo_itemspendinguserchanges'],

    bodyPadding: 5,
    layout: 'anchor',
    defaults: {
        anchor: '100%',
        bodyStyle: 'background:transparent;'
    },

    initComponent: function() {
        this.callParent(arguments);

        // Show or hide details based on parameter 'detailsOnStart'
        if (this.detailsOnStart) {
            this.showDetails();
        } else {
            this.hideDetails();
        }
    },

    /**
     * Adds a panel for each pending version. Also shows link to hide details
     * again.
     * Parameters 'detailData' and 'itemModel' need to be available, should be
     * passed on init.
     */
    showDetails: function() {

        if (this.detailData && this.itemModel) {

            // Remove any existing panels
            this.removeAll();

            // Create a store with all pending changes and load the data
            var pendingStore = Ext.create('Ext.data.Store', {
                model: this.itemModel,
                data: this.detailData,
                proxy: {
                    type: 'memory',
                    reader: {
                        type: 'json'
                    }
                }
            });
            pendingStore.load();

            // Loop through store to collect a panel for each record
            var pendingPanels = [];
            pendingStore.each(function(record) {
                pendingPanels.push({
                    xtype: 'lo_activitypanel',
                    contentItem: record,
                    border: 0,
                    bodyPadding: 0
                });
            });

            // Add the panels all at once (layout needs to be done only once)
            this.add(pendingPanels);

            // Add panel to hide the details again
            this.add({
                name: 'hideDetails',
                html: '<a href="#" class="itemspendinguserchanges_hidedetails">'
                    + 'Hide changes</a>',
                margin: '5 0 0 0',
                border: 0
            });
        }
    },

    /**
     * Hides all details and puts a link to show details.
     */
    hideDetails: function() {
        this.removeAll();
        this.add({
            name: 'showDetails',
            html: 'There are changes pending. <a href="#" '
                + 'class="itemspendinguserchanges_showdetails">Show changes</a>',
            border: 0
        });
    }
});