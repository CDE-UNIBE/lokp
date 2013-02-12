Ext.define('Lmkp.controller.moderation.CompareReview', {
    extend: 'Ext.app.Controller',

    stores: [
        'CompareInvolvements',
        'CompareTagGroups',
        'CompareVersions',
        'CompareMetadata',
        'ReviewDecisions'
    ],

    stringFunctions: null,
    missingKeys: null,

    refs: [
        {
            ref: 'compareWindow',
            selector: 'window[name=compareWindow]'
        }, {
            ref: 'comparePanel',
            selector: 'lo_moderatorcomparereview'
        }, {
            ref: 'refVersionCombobox',
            selector: 'lo_moderatorcomparereview combobox[itemId=cbRefVersion]'
        }, {
            ref: 'newVersionCombobox',
            selector: 'lo_moderatorcomparereview combobox[itemId=cbNewVersion]'
        }, {
            ref: 'refMetadataPanel',
            selector: 'lo_moderatorcomparereview panel[itemId=refMetadataPanel]'
        }, {
            ref: 'newMetadataPanel',
            selector: 'lo_moderatorcomparereview panel[itemId=newMetadataPanel]'
        }, {
            ref: 'reviewFormPanel',
            selector: 'lo_moderatorcomparereview form[itemId=reviewFormPanel]'
        }, {
            ref: 'compareButton',
            selector: 'lo_moderatorcomparereview button[itemId=compareButton]'
        }, {
            ref: 'reviewButton',
            selector: 'lo_moderatorcomparereview button[itemId=reviewButton]'
        }, {
            ref: 'recalculationNotice',
            selector: 'lo_moderatorcomparereview panel[itemId=recalculationNotice]'
        }, {
            ref: 'reviewCommentTextarea',
            selector: 'lo_moderatorcomparereview textarea[itemId=reviewCommentTextarea]'
        }, {
            ref: 'reviewDecisionCombobox',
            selector: 'lo_moderatorcomparereview combobox[name=review_decision]'
        }
    ],

    init: function() {
        this.control({
            'lo_moderatorcomparereview gridpanel gridcolumn[name=compareGridColumn]': {
                afterrender: this.onCompareColumnAfterRender
            },
            'lo_moderatorcomparereview combobox[itemId=cbRefVersion]': {
                select: this.onVersionComboboxSelectionChange
            },
            'lo_moderatorcomparereview combobox[itemId=cbNewVersion]': {
                select: this.onVersionComboboxSelectionChange
            },
            'lo_moderatorcomparereview button[itemId=compareRefreshButton]': {
                click: this.onVersionComboboxSelectionChange
            },
            'lo_moderatorcomparereview button[itemId=compareLinkButton]': {
                click: this.onCompareLinkButtonClick
            },
            'lo_moderatorcomparereview button[itemId=reviewButton]': {
                click: this.onReviewButtonClick
            },
            'lo_moderatorcomparereview button[itemId=compareButton]': {
                click: this.onCompareButtonClick
            },
            'lo_moderatorcomparereview': {
                render: this.onCompareViewRender
            },
            'lo_moderatorcomparereview button[itemId=reviewSubmitButton]': {
                click: this.onReviewSubmitButtonClick
            },
            'lo_moderatorcomparereview button[itemId=editButton]': {
                click: this.onEditButtonClick
            },
            'lo_moderatorcomparereview button[itemId=windowCloseButton]': {
                click: this.onWindowCloseButtonClick
            },
            'lo_moderatorcomparereview gridpanel templatecolumn[itemId=compareGridReviewableColumn]': {
                afterrender: this.onCompareGridReviewableColumnAfterRender
            }
        });
        this.stringFunctions = Ext.create('Lmkp.utils.StringFunctions');
    },

    onCompareViewRender: function() {
        var panel = this.getComparePanel();
        if (panel.action == 'review') {
            var formpanel = this.getReviewFormPanel();
            if (formpanel) {
                formpanel.setVisible(true);
            }
            var compareButton = this.getCompareButton();
            if (compareButton) {
                compareButton.setVisible(true);
            }
            var reviewButton = this.getReviewButton();
            if (reviewButton) {
                reviewButton.setVisible(false);
            }
        }
    },

    updateMetaPanels: function(metaModelInstance) {
        var template = new Ext.Template(
            '<b>' + Lmkp.ts.msg('gui_version') + '</b>: {0}<br/>' +
            '<b>' + Lmkp.ts.msg('gui_timestamp') + '</b>: {1}<br/>' +
            '<b>' + Lmkp.ts.msg('gui_user') + '</b>: {2}'
        );
        var refPanel = this.getRefMetadataPanel();
        var newPanel = this.getNewMetadataPanel();
        if (refPanel && newPanel) {
            refPanel.update(template.apply([
                metaModelInstance.get('ref_version'),
                this.stringFunctions._formatTimestamp(metaModelInstance.get('ref_timestamp')),
                metaModelInstance.get('ref_username')
            ]));
            newPanel.update(template.apply([
                metaModelInstance.get('new_version'),
                this.stringFunctions._formatTimestamp(metaModelInstance.get('new_timestamp')),
                metaModelInstance.get('new_username')
            ]));
        }

        var recalcNotice = this.getRecalculationNotice();
        if (metaModelInstance.get('recalculated')
            && this.getComparePanel().action == 'review' && recalcNotice) {
            recalcNotice.setVisible(true);
        } else if (recalcNotice) {
            recalcNotice.setVisible(false);
        }
    },

    reloadCompareTagGroupStore: function(action, type, uid, refVersion, newVersion) {

        var me = this;
        me.missingKeys = null;
        var win = this.getCompareWindow();

        if (win) {
            win.setLoading(true);
        }

        var url = this._getUrl('json', action, type, uid, refVersion, newVersion);

        if (url) {
            Ext.Ajax.request({
                url: url,
                success: function(response){
                    var data = Ext.JSON.decode(response.responseText);

                    if (data.success == false) {
                        // Intercept normal loading process if there is an error
                        // message from the server.
                        var infoWindow = Ext.create('Lmkp.utils.MessageBox');
                        infoWindow.alert(
                            Lmkp.ts.msg('feedback_information'),
                            data.msg
                        );

                        if (win) {
                            win.close();
                        }

                    } else {
                        me.getCompareTagGroupsStore().loadRawData(data);
                        me.getCompareInvolvementsStore().loadRawData(data);
                        me.getCompareVersionsStore().loadRawData(data);

                        // Clear any remaining filter on comboboxes
                        me.getCompareVersionsStore().clearFilter(true);

                        var mStore = me.getCompareMetadataStore();
                        mStore.loadRawData(data);

                        // Metadata
                        var metadata = mStore.first();
                        me.updateMetaPanels(metadata);

                        if (action == 'review') {
                            // For reviews, the left combobox always shows just the
                            // active version while the left shows only pending
                            // versions. To do this filtering, it is necessary to
                            // clone the store of the comboboxes.
                            var originalStore = me.getNewVersionCombobox().getStore();
                            var copyStore = me.deepCloneStore(originalStore);

                            originalStore.filter('status', 1);
                            if (originalStore.getCount() == 0) {
                                // If there are no pending versions (all reviewed),
                                // switch back to compare view
                                me.onCompareButtonClick();
                            }

                            copyStore.filter('status', 2);
                            if (copyStore.getCount() > 0) {
                                // There is no active version (for example when
                                // reviewing first version). Use the same store for
                                // both comboboxes
                                me.getRefVersionCombobox().bindStore(copyStore);
                            }
                            
                            // Add missing keys
                            if (data['missing_keys']) {
                            	var mk = data['missing_keys'];
                            	me.missingKeys = mk;
                            	var tgStore = me.getCompareTagGroupsStore();
                            	for (var k=0; k<mk.length; k++) {
                                    tgStore.add({
                                        'new': {
                                            'class': 'missing',
                                            'tags': [{
                                                'key': mk[k],
                                                'value': Lmkp.ts.msg('gui_unknown')
                                            }]
                                        }
                                    });
                            	}
                            }

                            me.getRefVersionCombobox().setReadOnly(true);
                        } else if (action == 'compare') {
                            if (me.getCompareVersionsStore().find('status', 1) == -1) {
                                // No (more) pending, disable review button
                                me.getReviewButton().disable();
                            }
                            me.getRefVersionCombobox().bindStore(
                                me.getCompareVersionsStore()
                            );
                            me.getRefVersionCombobox().setReadOnly(false);
                        }

                        // Comboboxes
                        me.getRefVersionCombobox().setValue(metadata.get('ref_version'));
                        me.getNewVersionCombobox().setValue(metadata.get('new_version'));

                        if (win) {
                            win.setLoading(false);
                        }
                    }
                }
            });
        }
    },

    onReviewSubmitButtonClick: function(button) {
        var me = this;
        var form = button.up('form').getForm();
        var infoWindow = Ext.create('Lmkp.utils.MessageBox');

        // Prepare additional parameters (not in form)
        var version = this.getNewVersionCombobox().getValue();
        var mData = this.getCompareMetadataStore().first();
        var identifier = mData.get('identifier');
        var type = mData.get('type');
        
        // Missing keys
        var reviewCombobox = this.getReviewDecisionCombobox();
        if (this.missingKeys && reviewCombobox && reviewCombobox.getValue() == 1) {
        	var winMissingKeys = Ext.create('Ext.window.Window', {
                title: Lmkp.ts.msg('moderator_review-not-possible'),
                bodyPadding: 10,
                modal: true,
                width: 300,
                html: Lmkp.ts.msg('moderator_missing-mandatory-keys'),
                buttons: [
                    {
                        text: Lmkp.ts.msg('button_ok'),
                        handler: function() {
                            winMissingKeys.close();
                        }
                    }
                ]
            }).show();
        } else if (form && version && identifier && type) {
            form.submit({
                url: '/' + type + '/review',
                params: {
                    version: version,
                    identifier: identifier
                },
                success: function(form, action) {
                    var result = Ext.JSON.decode(action.response.responseText);
                    infoWindow.alert(
                        Lmkp.ts.msg('feedback_success'),
                        result.msg,
                        function() {
                            // Refresh the panel
                            me.reloadCompareTagGroupStore(
                                'review', type, identifier
                            );
                            // Also clear review comment
                            me.getReviewCommentTextarea().reset();

                            // Also refresh the list with pending versions
                            var controller = me.getController('moderation.Pending');
                            if (controller) {
                                if (type == 'activities') {
                                    controller.getPendingActivityGridStore().load();
                                } else if (type == 'stakeholders') {
                                    controller.getPendingStakeholderGridStore().load();
                                }
                            }
                        }
                    );
                },
                failure: function(form, action) {
                    var result = Ext.JSON.decode(action.response.responseText);
                    infoWindow.alert(
                        Lmkp.ts.msg('feedback_failure'),
                        result.msg
                    );
                }
            });
        }
    },

    onCompareGridReviewableColumnAfterRender: function(comp) {
        var me = this;
        var review = this.getComparePanel()
            && this.getComparePanel().action == 'review';
        comp.renderer = function(value, metaData, record) {
            if (review) {
                var reviewable = record.get('reviewable');
                if (reviewable == -1) {
                    // Stakeholder was not found
                    return '<img src="/static/img/exclamation.png" style="cursor:pointer;" title="' + Lmkp.ts.msg('tooltip_review-involvement-not-possible') + '">';
                } else if (reviewable == -2) {
                    // Stakeholder has no active version
                    return '<img src="/static/img/exclamation.png" style="cursor:pointer;" title="' + Lmkp.ts.msg('tooltip_review-involvement-not-possible') + '">';
                } else if (reviewable == -3) {
                    // Activities cannot be reviewed from Stakeholder's side
                    return '<img src="/static/img/exclamation.png" style="cursor:pointer;" title="' + Lmkp.ts.msg('tooltip_review-involvement-not-possible') + '">';
                } else if (reviewable > 0) {
                    // Involvement can be reviewed
                    return '<img src="/static/img/accept.png" title="' + Lmkp.ts.msg('tooltip_review-involvement-possible') + '">';
                }
            } else {
                var data = record.get('new');
                if (data && data['class']) {
                    metaData.tdCls = data['class'];
                }
            }
            return '';
        }

        if (review) {
            comp.addListener('click', function(a, b, c, d, e, f) {
                var record = f;
                var data = record.get('new');
                if (record && record.get('reviewable') == -2
                    && data && data.identifier) {
                    var winError2 = Ext.create('Ext.window.Window', {
                        title: Lmkp.ts.msg('moderator_review-not-possible'),
                        bodyPadding: 10,
                        modal: true,
                        width: 300,
                        html: Lmkp.ts.msg('moderator_stakeholder-has-no-active-version'),
                        buttons: [
                            {
                                text: Lmkp.ts.msg('button_ok'),
                                handler: function() {
                                    winError2.close();
                                }
                            }, {
                                text: Lmkp.ts.msg('moderator_review-stakeholder'),
                                handler: function() {
                                    // Refresh the panel
                                    me.reloadCompareTagGroupStore(
                                        'review', 'stakeholders', data.identifier
                                    );
                                    winError2.close();
                                }
                            }
                        ]
                    }).show();
                } else if (record && record.get('reviewable') == -3
                    && data && data.identifier) {
                    var winError3 = Ext.create('Ext.window.Window', {
                        title: Lmkp.ts.msg('moderator_review-not-possible'),
                        bodyPadding: 10,
                        modal: true,
                        width: 300,
                        html: Lmkp.ts.msg('moderator_review-activity-side-of-involvement-first'),
                        buttons: [
                            {
                                text: Lmkp.ts.msg('button_ok'),
                                handler: function() {
                                    winError3.close();
                                }
                            }, {
                                text: Lmkp.ts.msg('moderator_review-activity'),
                                handler: function() {
                                    // Refresh the panel
                                    me.reloadCompareTagGroupStore(
                                        'review', 'activities', data.identifier
                                    );
                                    winError3.close();
                                }
                            }
                        ]
                    }).show();
                }
            });
        }
    },

    onCompareColumnAfterRender: function(comp) {
        comp.renderer = function(value, metaData, record) {
            if (value && value.tags) {
                metaData.tdCls = value['class'];
                var html = "";
                for(var i = 0; i < value.tags.length; i++){
                    var tag = value.tags[i];
                    var prefix = "";
                    if(value['class'] == 'add' || value['class'] == 'add involvement'){
                        prefix += "+ ";
                    } else if (value['class'] == 'remove' || value['class'] == 'remove involvement'){
                        prefix += "- ";
                    } else if (value['class'] == 'missing') {
                    	prefix += '? ';
                    	metaData.tdAttr = 'data-qtip="' + Lmkp.ts.msg('tooltip_missing-mandatory-key') + '"';
                    }
                    html += "<div>" + prefix + tag.key + ": " + tag.value + "</div>";
                }
                if (value['class'] == 'add involvement'
                    || value['class'] == 'remove involvement') {
                    metaData.tdAttr = 'data-qtip="' + Lmkp.ts.msg('tooltip_not-all-attributes-shown') + '"';
                }
                return html;
            }
        }
    },

    onVersionComboboxSelectionChange: function() {
        var mData = this.getCompareMetadataStore().first();
        this.reloadCompareTagGroupStore(
            this.getComparePanel().action,
            mData.get('type'),
            mData.get('identifier'),
            this.getRefVersionCombobox().getValue(),
            this.getNewVersionCombobox().getValue()
        );
    },

    onCompareLinkButtonClick: function() {
        var mData = this.getCompareMetadataStore().first();
        var url = this._getUrl(
            'html',
            this.getComparePanel().action,
            mData.get('type'),
            mData.get('identifier'),
            this.getRefVersionCombobox().getValue(),
            this.getNewVersionCombobox().getValue()
        );
        Ext.create('Lmkp.utils.PermalinkWindow', {
            url: url
        }).show();
    },

    onCompareButtonClick: function() {

        var win = this.getCompareWindow();
        if (!win) {
            win = this._createWindow();
            win.show();
        } else {
            win.removeAll();
        }

        var mData = this.getCompareMetadataStore().first();
        var type = mData.get('type');
        var identifier = mData.get('identifier');

        var title = '';
        if (type == 'activities') {
            title = Lmkp.ts.msg('activities_compare-versions').replace('{0}', this.stringFunctions._shortenIdentifier(identifier));
        } else if (type == 'stakeholders') {
            title = Lmkp.ts.msg('stakeholders_compare-versions').replace('{0}', this.stringFunctions._shortenIdentifier(identifier));
        }

        win.setLoading(true);
        win.setTitle(title);
        win.add({
            xtype: 'lo_moderatorcomparereview',
            action: 'compare'
        });

        this.reloadCompareTagGroupStore(
            'compare',
            type,
            identifier
        );
    },

    onReviewButtonClick: function() {
        var mData = this.getCompareMetadataStore().first();
        var win = this.getCompareWindow();
        if (!win) {
            win = this._createWindow();
            win.show();
        } else {
            win.removeAll();
        }

        var type = mData.get('type');
        var identifier = mData.get('identifier');

        var title = '';
        if (type == 'activities') {
            title = Lmkp.ts.msg('activities_review-versions').replace('{0}', this.stringFunctions._shortenIdentifier(identifier));
        } else if (type == 'stakeholders') {
            title = Lmkp.ts.msg('stakeholders_review-versions').replace('{0}', this.stringFunctions._shortenIdentifier(identifier));
        }

        win.setLoading(true);
        win.setTitle(title);
        win.add({
            xtype: 'lo_moderatorcomparereview',
            action: 'review'
        });

        this.reloadCompareTagGroupStore(
            'review',
            type,
            identifier
        );
    },

    onEditButtonClick: function() {

        // Set a loading mask
        var win = this.getCompareWindow();
        win.setLoading(true);

        // Collect needed values from metadata store
        var mData = this.getCompareMetadataStore().first();
        var type = mData.get('type');
        var identifier = mData.get('identifier');
        var version = mData.get('new_version');

        // Activity or Stakeholder?
        var model;
        if (type == 'activities') {
            model = 'Lmkp.model.Activity';
        } else if (type == 'stakeholders') {
            model = 'Lmkp.model.Stakeholder';
        }

        // Simulate a store to load the item to edit
        var store;
        if (type && identifier && version && model) {
            var url = '/' + type + '/json/' + identifier;
            store = Ext.create('Ext.data.Store', {
                model: model,
                proxy: {
                    type: 'ajax',
                    url: url,
                    extraParams: {
                        'involvements': 'full',
                        'versions': version
                    },
                    reader: {
                        type: 'json',
                        root: 'data'
                    }
                }
            });
        }

        // Use the controller to show the edit window
        var controller = this.getController('activities.NewActivity');
        if (store) {
            store.load(function(records, operation, success) {
                if (records.length == 1) {
                    var record = records[0];

                    if (type == 'activities') {
                        controller.showNewActivityWindow(record);
                    } else if (type == 'stakeholders') {
                        controller.showNewStakeholderWindow(record);
                    }
                }
                win.setLoading(false);
            });
        } else {
            win.setLoading(false);
        }
    },

    onWindowCloseButtonClick: function() {
        var win = this.getCompareWindow();
        win.close();
    },

    _createWindow: function(title) {

        // Window parameters
        var buffer = 50; // Minimal blank space at the sides of the window
        var defaultHeight = 700; // Default height of the window
        var defaultWidth = 700; // Default width of the window

        var viewSize = Ext.getBody().getViewSize();
        var height = (viewSize.height > defaultHeight + buffer)
            ? defaultHeight : viewSize.height - buffer;
        var width = (viewSize.width > defaultWidth + buffer)
            ? defaultWidth : viewSize.width - buffer;

        var win = Ext.create('Ext.window.Window', {
            name: 'compareWindow',
            title: title,
            layout: 'fit',
            border: false,
            height: height,
            width: width,
            modal: true
        });
        return win;
    },

    _getUrl: function(output, action, type, uid, refVersion, newVersion) {
        if (output && action && type && uid) {
            var url;
            if (output == 'json') {
                url = '/' + type + '/' + action + '/json/' + uid;
            } else if (output == 'html') {
                url = '/moderation/' + type + '/' + uid
            }
            if (refVersion && newVersion && output == 'json') {
                url += '/' + refVersion + '/' + newVersion;
            } else if (!refVersion && newVersion && output == 'json') {
                // Special case: Nothing is selected on the left side (brand new
                // object with multiple pending versions)
                url += '/0/' + newVersion;
            }
            return url;
        } else {
            return null;
        }
    },

    deepCloneStore: function(source) {
        var target = Ext.create ('Ext.data.Store', {
            model: source.model
        });

        Ext.each (source.getRange (), function (record) {
            var newRecordData = Ext.clone (record.copy().data);
            var model = new source.model (newRecordData, newRecordData.id);

            target.add (model);
        });

        return target;
    }

});