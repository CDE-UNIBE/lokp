Ext.define('Lmkp.view.activities.ActivityPanel', {
    extend: 'Lmkp.view.items.ItemPanel',
    alias: ['widget.lo_activitypanel'],

    requires: [
    'Lmkp.view.activities.TagGroupPanel',
    'Lmkp.view.activities.InvolvementPanel'
    ],

    bodyPadding: 5,
    layout: 'anchor',
    defaults: {
        margin: '3',
        anchor: '100%'
    },

    config: {
        editable: true
    },

    initComponent: function() {

        // Call parent first
        this.callParent(arguments);

        if (this.hiddenOriginal) {
            console.log("If you ever see this, it means that this is still needed ...");
            this.hideDetails();
        } else {
            this.showDetails();
        }
    },

    showDetails: function() {
        if (this.contentItem) {

            // Remove any existing panels
            this.removeAll();

            var editable = this.editable && Lmkp.editor;

            // If it is not an Activity Model ...
            if (!this.contentItem.isModel) {
                // ... create one. For this purpose, simulate a Store which
                // allows to access its TagGroups and Tags.
                var aStore = Ext.create('Ext.data.Store', {
                    model: 'Lmkp.model.Activity',
                    data: this.contentItem,
                    proxy: {
                        type: 'memory',
                        reader: {
                            type: 'json'
                        }
                    }
                });
                aStore.load();
                this.contentItem = aStore.getAt(0);
            }

            this._addStatusIndicator();

            // Get data and handle each TagGroup separately
            var taggroupStore = this.contentItem.taggroups();
            var tgPanels = [];
            taggroupStore.each(function(record) {
                tgPanels.push({
                    xtype: 'lo_taggrouppanel',
                    taggroup: record,
                    editable: editable
                });
            });
            // Add all panels at once (layout needs to be done only once)
            this.add(tgPanels);

            // Show involvements: Only show them if Activity is not deleted
            // (empty)
            if (!this.contentItem.isEmpty()) {
                var involvementStore = this.contentItem.involvements();
                var invPanels = [];
                involvementStore.each(function(record) {
                    invPanels.push({
                        xtype: 'lo_involvementpanel',
                        involvement: record,
                        involvement_type: 'stakeholder',
                        editable: editable
                    });
                });
                this.add(invPanels);
            }

            // Show link to hide original version if needed
            if (this.hiddenOriginal) {
                this.add({
                    name: 'hideDetails',
                    html: '<a href="#" class="itempanel_hidedetails">'
                    + 'Hide active version</a>',
                    margin: '5 0 0 0',
                    border: 0,
                    bodyStyle: 'background:transparent'
                });
            }

        } else {
            this.html = Lmkp.ts.msg('gui_unknown');
        }
    },

    hideDetails: function() {
        this.removeAll();
        this.add({
            name: 'showDetails',
            html: '<a href="#" class="itempanel_showdetails">'
            + 'Show active version</a>',
            border: 0,
            bodyStyle: 'background:transparent',
            margin: 0
        });
    },

    _getTaggroupPanels: function() {
        return this.query('lo_taggrouppanel');
    }
});