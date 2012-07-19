Ext.define('Lmkp.view.activities.DiffPanel', {
    extend: 'Ext.form.Panel',
    alias: ['widget.lo_diffpanel'],

    // General settings
    layout: 'anchor',
    defaults: {
        anchor: '100%',
        margin: 0,
        border: 0
    },
    border: 1,
    bodyPadding: 5,

    title: Lmkp.ts.msg('review-diff_title'),

    initComponent: function() {

        this.items = []


        if (this.diff && this.contentItem) {

            // Involvement is Activity or Stakeholder?
            var involvement_type = null;
            if (this.contentItem == 'activities') {
                involvement_type = 'stakeholder';
            } else if (this.contentItem == 'stakeholders') {
                involvement_type = 'activity';
            }

            // New attributes
            if (this.diff.new_attr) {
                for (var i in this.diff.new_attr) {
                    this.items.push({
                        xtype: 'fieldset',
                        collapsible: true,
                        collapsed: true,
                        border: 1,
                        title: '<span class="new">' +
                            Lmkp.ts.msg('review-diff_attr_added') + '</span>',
                        items: [
                            {
                                xtype: 'panel',
                                html: 'Coming soon ...'
                            }
                        ]
                    });
                }
            }
            // New involvements
            if (this.diff.new_inv) {
                for (var j in this.diff.new_inv) {
                    this.items.push({
                        xtype: 'fieldset',
                        collapsible: true,
                        collapsed: true,
                        border: 1,
                        title: '<span class="new">' +
                            Lmkp.ts.msg('review-diff_inv_added') + '</span>',
                        items: [
                            {
                                xtype: 'lo_involvementpanel',
                                involvement: this.diff.new_inv[j],
                                involvement_type: involvement_type,
                                title: null,
                                border: 0,
                                bodyPadding: 0
                            }
                        ]
                    });
                }
            }
            // Deleted attributes
            if (this.diff.old_attr) {
                for (var k in this.diff.old_attr) {
                    this.items.push({
                        xtype: 'fieldset',
                        collapsible: true,
                        collapsed: true,
                        border: 1,
                        title: '<span class="deleted">' +
                            Lmkp.ts.msg('review-diff_attr_deleted') + '</span>',
                        items: [
                            {
                                xtype: 'panel',
                                html: 'Coming soon ...'
                            }
                        ]
                    });
                }
            }
            // Deleted involvements
            if (this.diff.old_inv) {
                for (var l in this.diff.old_inv) {
                    this.items.push({
                        xtype: 'fieldset',
                        collapsible: true,
                        collapsed: true,
                        border: 1,
                        title: '<span class="deleted">' +
                            Lmkp.ts.msg('review-diff_inv_deleted') + '</span>',
                        items: [
                            {
                                xtype: 'lo_involvementpanel',
                                involvement: this.diff.old_inv[l],
                                involvement_type: involvement_type,
                                title: null,
                                border: 0,
                                bodyPadding: 0
                            }
                        ]
                    });
                }
            }
        }
        this.callParent(arguments);
    }

});