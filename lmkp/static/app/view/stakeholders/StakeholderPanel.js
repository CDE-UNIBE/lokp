Ext.define('Lmkp.view.stakeholders.StakeholderPanel', {
    extend: 'Ext.panel.Panel',
    alias: ['widget.lo_stakeholderpanel'],

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