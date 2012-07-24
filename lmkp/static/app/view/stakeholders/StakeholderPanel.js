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

        var me = this;
        
        // Call parent first
        this.callParent(arguments);

        if (this.contentItem) {

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
            taggroupStore.each(function(record) {
                me.add({
                    editable: this.editable,
                    taggroup: record,
                    xtype: 'lo_taggrouppanel'
                });
            });

            // Show involvements
            var involvementStore = this.contentItem.involvements();
            for (var k=0; k<involvementStore.count(); k++) {
                this.add({
                    xtype: 'lo_involvementpanel',
                    involvement: involvementStore.getAt(k),
                    involvement_type: 'activity'
                });
            }
        } else {
            this.html = Lmkp.ts.msg('unknown');
        }
    }
});