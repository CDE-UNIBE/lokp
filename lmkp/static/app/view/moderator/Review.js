Ext.define('Lmkp.view.moderator.Review', {
    extend: 'Ext.panel.Panel',
    alias: ['widget.lo_moderatorreviewpanel'],

    requires: [
    'Lmkp.view.activities.ActivityPanel',
    'Lmkp.view.stakeholders.StakeholderPanel',
    'Lmkp.view.activities.ChangesetPanel',
    'Lmkp.view.activities.DiffPanel'
    ],

    bodyPadding: 5,
    layout: {
        type: 'anchor'
    },
    defaults: {
        margin: '0 0 5 0',
        anchor: '100%'
    },
    autoScroll: true,

    initComponent: function() {

        // Call parents first
        this.callParent(arguments);

        // Show initial content
        this.showInitialContent();
    },

    showInitialContent: function() {

        // Remove any existing panels
        this.removeAll();

        // Show initial panel
        this.add({
            xtype: 'panel',
            name: 'review_initial',
            html: Lmkp.ts.msg('reviewpanel-empty_msg'),
            border: 0
        });
    },

    updateContent: function(data, type) {

        // Activity or Stakeholder?
        var xtype = null;
        if (type == 'activities') {
            xtype = 'lo_activitypanel'
        } else if (type == 'stakeholders') {
            xtype = 'lo_stakeholderpanel'
        }

        // Remove any existing panels
        this.removeAll();
        
        // Loop through all data to collect all 'pending' items. Also remember
        // which is the active version
        var pending = [];
        var active_version = null;
        for (var i in data.data) {
            if (data.data[i].status == 'pending') {
                pending.push({
                    'current_version': data.data[i].version,
                    'previous_version': data.data[i].previous_version
                });
            }
            if (data.data[i].status == 'active') {
                active_version = data.data[i].version;
            }
        }

        // Show a notice if more than one change pending for same item
        if (pending.length >= 2) {
            this.add({
                bodyPadding: 5,
                html: Lmkp.ts.msg('reviewpanel-multiple_changes'),
                bodyCls: 'notice'
            });
        }

        // Show panels
        for (var j in pending) {
            for (var k in data.data) {
                // First show panel with pending item
                if (data.data[k].version == pending[j].current_version) {
                    // Show notice if previous version is not active
                    var noticepanel = null;
                    if (data.data[k].previous_version != null &&
                        data.data[k].previous_version != active_version) {
                        noticepanel = {
                            xtype: 'panel',
                            bodyPadding: 5,
                            html: Lmkp.ts.msg('reviewpanel-not_active_changed'),
                            bodyCls: 'notice'
                        }
                    }
                    this.add({
                        xtype: 'lo_changesetpanel',
                        // Panel data
                        timestamp: data.data[k].timestamp,
                        version: data.data[k].version,
                        previous_version: data.data[k].previous_version,
                        username: data.data[k].username,
                        userid: data.data[k].userid,
                        additionalPanelBottom: {
                            xtype: xtype,
                            contentItem: data.data[k],
                            border: 0,
                            editable: false
                        },
                        additionalPanelTop: noticepanel,
                        // Panel settings
                        title: Lmkp.ts.msg('reviewpanel-pending_title'),
                        collapsible: true
                    });
                    // Show diff panel
                    if (data.data[k].diff) {
                        this.add({
                            xtype: 'lo_diffpanel',
                            diff: data.data[k].diff,
                            contentItem: type
                        });
                    }
                }
                // Then show panel with previous version
                if (data.data[k].version ==
                    pending[j].previous_version) {
                    this.add({
                        xtype: 'lo_changesetpanel',
                        // Panel data
                        timestamp: data.data[k].timestamp,
                        version: data.data[k].version,
                        previous_version: data.data[k].previous_version,
                        username: data.data[k].username,
                        userid: data.data[k].userid,
                        additionalPanelBottom: {
                            xtype: xtype,
                            contentItem: data.data[k],
                            border: 0,
                            editable: false
                        },
                        // Panel settings
                        title: Lmkp.ts.msg('reviewpanel-previous_title'),
                        collapsible: true,
                        collapsed: true
                    });
                }
            }

            // Show panel for review decision
            var rdStore = Ext.create('Lmkp.store.ReviewDecisions').load();
            this.add({
                xtype: 'form',
                url: type + '/review',
                border: 0,
                buttonAlign: 'right',
                items: [
                    {
                        xtype: 'panel',
                        layout: 'hbox',
                        border: 0,
                        items: [
                            {
                                xtype: 'combobox',
                                store: rdStore,
                                name: 'review_decision',
                                queryMode: 'local',
                                displayField: 'name',
                                valueField: 'id',
                                fieldLabel: 'Review decision',
                                allowBlank: false,
                                flex: 1,
                                margin: '0 5 0 0'
                            }, {
                                xtype: 'checkbox',
                                fieldLabel: 'Add comment',
                                name: 'comment_checkbox',
                                margin: '0 5 0 0'
                            }, {
                                xtype: 'button',
                                text: 'Submit',
                                name: 'review_submit',
                                store_type: type // helper parameter
                            }
                        ]
                    }, {
                        xtype: 'textarea',
                        name: 'comment_textarea',
                        width: '100%',
                        margin: '5 0 0 0',
                        hidden: true
                    }, {
                        xtype: 'hiddenfield',
                        name: 'identifier',
                        value: data.data[0].id
                    }, {
                        xtype: 'hiddenfield',
                        name: 'version',
                        value: pending[j].current_version
                    }
                ]
            });

            // If there are multiple changes, show spacer between them
            if (j != pending.length - 1) {
                this.add({
                    height: 20,
                    bodyCls: 'blank'
                });
            }
        }
    }
});