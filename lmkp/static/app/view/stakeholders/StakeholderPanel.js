Ext.define('Lmkp.view.stakeholders.StakeholderPanel', {
    extend: 'Ext.panel.Panel',
    alias: ['widget.lo_stakeholderpanel'],

    requires: [
    'Lmkp.view.activities.TagGroupPanel',
    'Lmkp.view.activities.InvolvementPanel'
    ],

    bodyPadding: 5,

    config: {
        editable: true
    },

    layout: 'anchor',
    
    defaults: {
        margin: '5 0 0 0',
        anchor: '100%'
    },

    initComponent: function() {
        
        // Call parent first
        this.callParent(arguments);

        if (this.contentItem) {
            var editable = this.editable;

            // If it is not a Stakeholder Model ...
            if (!this.contentItem.isModel) {
                // ... create one. For this purpose, simulate a Store which
                // allows to access its TagGroups and Tags.
                var shStore = Ext.create('Ext.data.Store', {
                    model: 'Lmkp.model.Stakeholder',
                    data: this.contentItem,
                    proxy: {
                        type: 'memory',
                        reader: {
                            type: 'json'
                        }
                    }
                });
                shStore.load();
                this.contentItem = shStore.getAt(0);
            }

            // Get data and handle each TagGroup separately
            var taggroupStore = this.contentItem.taggroups();
            var tgPanels = [];
            taggroupStore.each(function(record) {
                tgPanels.push({
                    editable: editable,
                    taggroup: record,
                    xtype: 'lo_taggrouppanel'
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
                    involvement_type: 'activity',
                    editable: editable
                });
            });
            this.add(invPanels);
        } else {
            this.html = Lmkp.ts.msg('unknown');
        }
    }
});