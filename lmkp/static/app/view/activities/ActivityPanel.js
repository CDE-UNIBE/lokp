Ext.define('Lmkp.view.activities.ActivityPanel', {
    extend: 'Ext.panel.Panel',
    alias: ['widget.lo_activitypanel'],

    requires: [
        'Lmkp.view.activities.TagGroupPanel',
        'Lmkp.view.activities.InvolvementPanel'
    ],

    bodyPadding: 5,
    layout: 'anchor',
    defaults: {
        margin: '5 0 0 0',
        anchor: '100%'
    },

    config: {
        editable: true
    },

    initComponent: function() {


        // Call parent first
        this.callParent(arguments);

        if (this.contentItem) {
            var editable = this.editable;

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

            // Show involvements
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
        } else {
            this.html = Lmkp.ts.msg('unknown');
        }
    },

    _getTaggroupPanels: function() {
        return this.query('lo_taggrouppanel');
    }
});