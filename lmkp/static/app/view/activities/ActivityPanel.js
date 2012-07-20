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

    initComponent: function() {

        var me = this;

        // Call parent first
        this.callParent(arguments);

        if (this.contentItem) {

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
            taggroupStore.each(function(record) {
                me.add({
                    xtype: 'lo_taggrouppanel',
                    taggroup: record
                });
            });

            // Show involvements
            var involvementStore = this.contentItem.involvements();
            for (var k=0; k<involvementStore.count(); k++) {
                this.add({
                    xtype: 'lo_involvementpanel',
                    involvement: involvementStore.getAt(k),
                    involvement_type: 'stakeholder'
                });
            }
        } else {
            this.html = Lmkp.ts.msg('unknown');
        }
    }
});