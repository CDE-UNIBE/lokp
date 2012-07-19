Ext.define('Lmkp.view.moderator.Review', {
    extend: 'Ext.panel.Panel',
    alias: ['widget.lo_moderatorreviewpanel'],

    requires: [
        'Lmkp.view.activities.ActivityPanel',
        'Lmkp.view.stakeholders.StakeholderPanel',
        'Lmkp.view.activities.ChangesetPanel'
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
    
    items: [{
        xtype: 'panel',
        name: 'review_initial',
        html: Lmkp.ts.msg('reviewpanel-empty_msg'),
        border: 0
    }],

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
                            border: 0
                        },
                        additionalPanelTop: noticepanel,
                        // Panel settings
                        title: Lmkp.ts.msg('reviewpanel-pending_title'),
                        collapsible: true
                    });
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
                            border: 0
                        },
                        // Panel settings
                        title: Lmkp.ts.msg('reviewpanel-previous_title'),
                        collapsible: true,
                        collapsed: true
                    });
                }
            }

            // If there are multiple changes, show spacer between them
            if (j != pending.length - 1) {
                this.add({
                    height: 10,
                    bodyCls: 'notice'
                });
            }
        }
    }
});