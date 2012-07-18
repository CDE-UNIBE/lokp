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

        // Call parent first
        this.callParent(arguments);

        if (this.activity) {

            // If it is not an Activity Model ...
            if (!this.activity.isModel) {
                // ... create one. For this purpose, simulate a Store which
                // allows to access its TagGroups and Tags.
                var aStore = Ext.create('Ext.data.Store', {
                    model: 'Lmkp.model.Activity',
                    data: this.activity,
                    proxy: {
                        type: 'memory',
                        reader: {
                            type: 'json'
                        }
                    }
                });
                aStore.load();
                this.activity = aStore.getAt(0);
            }

            // Get data
            var taggroupStore = this.activity.taggroups();

            // Handle each TagGroup separately
            for (var i=0; i<taggroupStore.count(); i++) {

                var tagStore = taggroupStore.getAt(i).tags();
                var tags = [];
                var main_tag = null;

                // Collect main tag and other tags
                for (var j=0; j<tagStore.count(); j++) {
                    if (taggroupStore.getAt(i).get('main_tag')
                        == tagStore.getAt(j).get('id')) {
                        main_tag = tagStore.getAt(j);
                    } else {
                        tags.push(tagStore.getAt(j));
                    }
                }

                this.add({
                    xtype: 'lo_taggrouppanel',
                    main_tag: main_tag,
                    tags: tags
                });
            }

            // Show involvements
            var involvementStore = this.activity.involvements();
            for (var k=0; k<involvementStore.count(); k++) {
                this.add({
                    xtype: 'lo_involvementpanel',
                    involvement: involvementStore.getAt(k)
                });
            }
        }
    }
});