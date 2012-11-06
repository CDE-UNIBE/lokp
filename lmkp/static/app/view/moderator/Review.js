Ext.define('Lmkp.view.moderator.Review', {
    extend: 'Ext.container.Container',
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
        //this.showInitialContent();
        this.updateContent(this.store, this.type);
    },

    updateContent: function(store, type) {

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
        store.each(function(record){
            if (record.get('status') == Lmkp.ts.msg('status_pending')) {
                pending.push({
                    'current_version': record.get('version'),
                    'previous_version': record.get('previous_version'),
                    'missing_keys': record.get('missing_keys')
                });
            }
            if (record.get('status') == Lmkp.ts.msg('status_active')) {
                active_version = record.get('version');
            }
        }, this);

        // Show a notice if more than one change pending for same item
        if (pending.length >= 2) {
            this.add({
                bodyPadding: 5,
                html: Lmkp.ts.msg('moderator_multiple-changes-pending'),
                bodyCls: 'notice'
            });
        }

        // Show panels
        for (var j in pending) {
            store.each(function(record){
                // First show panel with pending item
                if (record.get('version') == pending[j].current_version) {
                    // Show notice if previous version is not active
                    var noticepanel = null;
                    if (record.get('previous_version') != null &&
                        record.get('previous_version') != active_version) {
                        noticepanel = {
                            xtype: 'panel',
                            bodyPadding: 5,
                            html: Lmkp.ts.msg('moderator_changes-not-based-on-active'),
                            bodyCls: 'notice'
                        }
                    }
                    this.add({
                        xtype: 'lo_changesetpanel',
                        // Panel data
                        timestamp: record.get('timestamp'),
                        version: record.get('version'),
                        previous_version: record.get('previous_version'),
                        username: record.get('username'),
                        userid: record.get('userid'),
                        additionalPanelBottom: {
                            xtype: xtype,
                            contentItem: record,
                            border: 0,
                            editable: true
                        },
                        additionalPanelTop: noticepanel,
                        // Panel settings
                        title: Lmkp.ts.msg('moderator_pending-version-title'),
                        collapsible: true
                    });
                    // Show diff panel
                    if (record.get('diff')) {
                        this.add({
                            xtype: 'lo_diffpanel',
                            diff: record.get('diff'),
                            contentItem: type
                        });
                    }
                }
                // Then show panel with previous version
                if (record.get('version') ==
                    pending[j].previous_version) {
                    this.add({
                        xtype: 'lo_changesetpanel',
                        // Panel data
                        timestamp: record.get('timestamp'),
                        version: record.get('version'),
                        previous_version: record.get('previous_version'),
                        username: record.get('username'),
                        userid: record.get('userid'),
                        additionalPanelBottom: {
                            xtype: xtype,
                            contentItem: record,
                            border: 0,
                            editable: false
                        },
                        // Panel settings
                        title: Lmkp.ts.msg('gui_previous-version'),
                        collapsible: true,
                        collapsed: true
                    });
                }
            }, this);


            // Show panel for review decision.
            var rdStore = Ext.create('Lmkp.store.ReviewDecisions').load();
            this.add({
                buttons: [{
                    iconCls: 'save-button',
                    itemId: 'reviewSubmitButton',
                    name: 'review_submit',
                    scale: 'medium',
                    scope: this,
                    store_type: type, // helper parameter
                    text: Lmkp.ts.msg('button_submit'),
                    xtype: 'button'
                }],
                xtype: 'form',
                url: type + '/review',
                border: 0,
                buttonAlign: 'right',
                items: [{
                    store: rdStore,
                    name: 'review_decision',
                    queryMode: 'local',
                    displayField: 'name',
                    valueField: 'id',
                    fieldLabel: Lmkp.ts.msg('moderator_review-decision'),
                    allowBlank: false,
                    flex: 1,
                    margin: 3,
                    value: 1,
                    width: 400,
                    xtype: 'combobox'
                }, {
                    fieldLabel: Lmkp.ts.msg('moderator_review-comment'),
                    margin: 3,
                    name: 'comment_textarea',
                    width: 400,
                    xtype: 'textarea'
                }, {
                    xtype: 'hiddenfield',
                    name: 'identifier',
                    value: store.first().get('id')
                }, {
                    xtype: 'hiddenfield',
                    name: 'version',
                    value: pending[j].current_version
                }]
            });

            // Show notice and list with missing fields if not all mandatory
            // attributes are there.
            // @TODO: Make this work again ...
            if (pending[j].missing_keys.length > 0) {
                if (pending[j].missing_keys.length == 1 &&
                    pending[j].missing_keys[0] == 0) {
                    // Item is pending to be deleted
                    var html = 'This version is pending to be deleted. If '
                    + 'approved, it will no longer be visible.';
                } else {
                    // Show list of missing keys
                    var html = 'This version cannot be approved (set public) '
                    + 'because not all mandatory fields are there.'
                    + '<br/>Missing fields are:<ul>';
                    for (var mf in pending[j].missing_keys) {
                        html += '<li><b>' + pending[j].missing_keys[mf] + '</b></li>';
                    }
                    html += '</ul>';
                }
                
                this.add({
                    xtype: 'panel',
                    html: html,
                    bodyCls: 'notice',
                    bodyPadding: 5
                });
            }

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