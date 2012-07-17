Ext.define('Lmkp.view.editor.Detail', {
    extend: 'Ext.tab.Panel',
    alias: ['widget.lo_editordetailpanel'],

    config: {
        // The currently shown activity in this panel or null if no activity
        // is shown
        current: {}
    },
	
    plain: true,
    activeTab: 0,
    defaults: {
        autoScroll: true
    },

    items: [{
        title: 'Details',
        xtype: 'activityDetailTab'
    }, {
        title: 'History',
        xtype: 'activityHistoryTab'
    }],

    initComponent: function() {
        this.callParent(arguments);
    },

    populateDetailsTab: function(panel, data) {

        if (data.length > 0) {

            // Set the current selection to current
            this.current = data[0];

            // remove initial text if still there
            if (panel.down('panel[name=details_initial]')) {
                panel.remove(panel.down('panel[name=details_initial]'));
            }

            // remove old panels
            while (panel.down('taggrouppanel')) {
                panel.remove(panel.down('taggrouppanel'));
            }

            // remove comment panel
            if (panel.down('commentpanel')) {
                panel.remove(panel.down('commentpanel'));
            }

            // get data
            var taggroupStore = data[0].taggroups();

            // add panel for each TagGroup
            for (var i=0; i<taggroupStore.count(); i++) {
                var tagStore = taggroupStore.getAt(i).tags();
                var tags = [];
                var main_tag = null;

                for (var j=0; j<tagStore.count(); j++) {

                    // check if it is main_tag
                    if (taggroupStore.getAt(i).get('main_tag') == tagStore.getAt(j).get('id')) {
                        main_tag = tagStore.getAt(j);
                    } else {
                        tags.push(tagStore.getAt(j));
                    }
                }

                // create panel
                var taggroupPanel = Ext.create('Lmkp.view.activities.TagGroupPanel', {
                    'main_tag': main_tag,
                    'tags': tags
                });
                // if user is logged in (Lmkp.toolbar != false), show edit button
                if (Lmkp.toolbar) {
                    //console.log("add docked");
                    taggroupPanel.addDocked({
                        dock: 'right',
                        xtype: 'toolbar',
                        items: [{
                            name: 'editTaggroup',
                            scale: 'small',
                            text: 'edit',
                            taggroup_id: i, // store local id (in taggroupStore) of current TagGroup
                            handler: function() {
                                var win = Ext.create('Lmkp.view.activities.NewTaggroupWindow', {
                                    activity_id: data[0].get('id'),
                                    version: data[0].get('version'),
                                    selected_taggroup: taggroupStore.getAt(this.taggroup_id)
                                });
                                win.show();
                            },
                            xtype: 'button'
                        }]
                    });
                }
                panel.add(taggroupPanel);
            }

            // add commenting panel
            var commentPanel = Ext.create('Lmkp.view.comments.CommentPanel', {
                'activity_id': data[0].get('id'),
                'comment_object': 'activity'
            });
            panel.add(commentPanel);

        /*panel.addDocked({
                id: 'top_toolbar',
                dock: 'top',
                xtype: 'toolbar',
                items: [
                '->',
                {
                    text: 'show all details',
                    handler: function() {
                        for (var i in panel.query('taggrouppanel')) {
                            panel.query('taggrouppanel')[i].toggleDetailButton(true);
                        }
                    }
                }, {
                    text: 'hide all details',
                    handler: function() {
                        for (var i in panel.query('taggrouppanel')) {
                            panel.query('taggrouppanel')[i].toggleDetailButton(false);
                        }
                    }
                }]
            });*/
        }
    },

    populateHistoryTab: function(panel, uid) {
        if (uid) {
            Ext.Ajax.request({
                url: '/activities/history/' + uid,
                success: function(response, opts) {

                    // remove initial text if still there
                    if (panel.down('panel[name=history_initial]')) {
                        panel.remove(panel.down('panel[name=history_initial]'));
                    }

                    // remove old panels
                    if (panel.down('panel[name=history_active]')) {
                        panel.remove(panel.down('panel[name=history_active]'));
                    }
                    if (panel.down('panel[name=history_deleted]')) {
                        panel.remove(panel.down('panel[name=history_deleted]'));
                    }
                    while (panel.down('panel[name=history_overwritten]')) {
                        panel.remove(panel.down('panel[name=history_overwritten]'));
                    }

                    // get data
                    var json = Ext.JSON.decode(response.responseText);
                    // prepare template
                    var tpl = new Ext.XTemplate(
                        '<tpl for="attrs">',
                        '<span class="{cls}"><b>{k}</b>: {v}<br/></span>',
                        '</tpl>',
                        '<p>&nbsp;</p>',
                        '<tpl if="deleted != null">',
                        'Deleted: <span class="deleted"><b>{deleted}</b></span>',
                        '<p>&nbsp;</p>',
                        '</tpl>',
                        '<p class="version_info">Version {version} created on {timestamp}.<br/>',
                        'Data provided by <a href="#" onclick="Ext.create(\'Lmkp.view.users.UserWindow\', { username: \'{username}\' }).show();">{username}</a> [userid: {userid}].<br/>',
                        'Additional source of information: {source}</p>'
                        );

                    // add panel for current version if there is one
                    if (json.data.active) {
                        // prepare data
                        var o = json.data.active;
                        var ts = Ext.Date.format(Ext.Date.parse(o.timestamp, "Y-m-d H:i:s.u"), "Y/m/d H:i");
                        var changes = Ext.JSON.decode(o.changes);

                        // first, add general data about activity and changeset
                        var data = {
                            username: o.username,
                            userid: o.userid,
                            source: o.source,
                            timestamp: ts,
                            version: o.version,
                            id: o.id,
                            activity_identifier: o.activity_identifier
                        }
                        // add all remaining data: the key/value pairs
                        attrs = []
                        for (attr in o) {
                            // do not add general data (again) and do not add 'changes'
                            if (!data[attr] && attr != 'changes') {
                                // default class
                                var cls = 'unchanged';
                                // check for changes and update class accordingly
                                if (changes[attr]) {
                                    cls = changes[attr];
                                }
                                attrs.push({
                                    k: attr,
                                    v: o[attr],
                                    cls: cls
                                });
                            }
                        }
                        data["attrs"] = attrs;
                        // check for deleted attributes
                        var deleted = []
                        for (var i in changes) {
                            if (changes[i] == 'deleted') {
                                deleted.push(i);
                            }
                        }
                        data["deleted"] = (deleted.length > 0) ? deleted.join(", ") : null;

                        // create panel
                        var activePanel = Ext.create('Ext.panel.Panel', {
                            name: 'history_active',
                            title: '[Current] Version ' + o.version + ' (' + ts + ')',
                            collapsible: true,
                            collapsed: true
                        });
                        // add panel and apply template
                        panel.add(activePanel);
                        tpl.overwrite(activePanel.body, data);
                    }

                    // add panel for deleted version if there is one
                    if (json.data.deleted) {
                        // prepare data
                        var o = json.data.deleted;
                        var ts = Ext.Date.format(Ext.Date.parse(o.timestamp, "Y-m-d H:i:s.u"), "Y/m/d H:i");

                        // first, add general data about activity and changeset
                        var data = {
                            username: o.username,
                            userid: o.userid,
                            source: o.source,
                            timestamp: ts,
                            version: o.version,
                            id: o.id,
                            activity_identifier: o.activity_identifier
                        }

                        // special template
                        var deletedTpl = new Ext.XTemplate(
                            '<span class="deleted"><b>Deleted</b></span>',
                            '<p>&nbsp;</p>',
                            '<p class="version_info">This activity was deleted on {timestamp} by <a href="#" onclick="Ext.create(\'Lmkp.view.users.UserWindow\', { username: \'{username}\' }).show();">{username}</a> [userid: {userid}].<br/>',
                            'Additional source of information: {source}</p>'
                            );

                        // create panel
                        var deletedPanel = Ext.create('Ext.panel.Panel', {
                            name: 'history_deleted',
                            title: '[Deleted] (' + ts + ')',
                            collapsible: true,
                            collapsed: true
                        });

                        // add panel and apply template
                        panel.add(deletedPanel);
                        deletedTpl.overwrite(deletedPanel.body, data);
                    }

                    // add panels for old versions if there are any
                    if (json.data.overwritten.length > 0) {
                        for (var i in json.data.overwritten) {
                            // prepare data
                            var o = json.data.overwritten[i];
                            var ts = Ext.Date.format(Ext.Date.parse(o.timestamp, "Y-m-d H:i:s.u"), "Y/m/d H:i");
                            var changes = Ext.JSON.decode(o.changes);
                            // first, add general data about activity and changeset
                            var data = {
                                username: o.username,
                                userid: o.userid,
                                source: o.source,
                                timestamp: ts,
                                version: o.version,
                                id: o.id,
                                activity_identifier: o.activity_identifier
                            };
                            // add all remaining data: the key/value pairs
                            attrs = [];
                            for (attr in o) {
                                // do not add general data (again) and do not add 'changes'
                                if (!data[attr] && attr != 'changes') {
                                    // default class
                                    var cls = 'unchanged';
                                    // check for changes and update class accordingly
                                    if (changes[attr]) {
                                        cls = changes[attr];
                                    }
                                    attrs.push({
                                        k: attr,
                                        v: o[attr],
                                        cls: cls
                                    });
                                }
                            }
                            data["attrs"] = attrs;
                            // check for deleted attributes
                            var deleted = []
                            for (var i in changes) {
                                if (changes[i] == 'deleted') {
                                    deleted.push(i);
                                }
                            }
                            data["deleted"] = (deleted.length > 0) ? deleted.join(", ") : null;
                            // create panel
                            var p = Ext.create('Ext.panel.Panel', {
                                name: 'history_overwritten',
                                title: 'Version ' + o.version + ' (' + ts + ')',
                                collapsible: true,
                                collapsed: true
                            });
                            panel.add(p);
                            tpl.overwrite(p.body, data);
                        }
                    }

                    // in case no active and no overwritten activities were found (this should never happen),
                    // show at least something.
                    // using the initial panel because this will be removed when selected the next activity
                    if (!json.data.active && !json.data.deleted && json.data.overwritten.length == 0) {
                        panel.add({
                            xtype: 'panel',
                            border: 0,
                            name: 'history_initial',
                            html: 'No history found for this activity',
                            collapsible: false,
                            collapsed: false
                        });
                    }

                    // layout does not seem to work if panel is expanded on start, therefore this is done
                    // after everything was added.
                    // TODO: find out why ...
                    if (activePanel) {
                        activePanel.toggleCollapse();
                    }
                    if (deletedPanel) {
                        deletedPanel.toggleCollapse();
                    }
                }
            });
        }
    }

});
