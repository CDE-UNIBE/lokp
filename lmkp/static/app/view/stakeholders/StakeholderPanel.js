Ext.define('Lmkp.view.stakeholders.StakeholderPanel', {
    extend: 'Lmkp.view.items.ItemPanel',
    alias: ['widget.lo_stakeholderpanel'],

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
            this.hideDetails();
        } else {
            this.showDetails();
        }
    },

    showDetails: function() {
        if (this.contentItem) {

            // Remove any existing panels
            this.removeAll();

            var editable = this.editable && Lmkp.toolbar != false;

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

            this._addStatusIndicator();
            
            /*if (this.contentItem.get('status') == 'pending') {
                this.add({
                    bodyCls: 'notice',
                    bodyPadding: 5,
                    html: 'You are seeing a pending version, which needs to be \n\
                        reviewed before it is publicly visible',
                    margin: '3 3 0 3'
                });
            }*/

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

            // Show involvements: Only show them if Stakeholder is not deleted
            // (empty)
            if (!this.contentItem.isEmpty()) {
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
            this.html = Lmkp.ts.msg('unknown');
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
    }
});