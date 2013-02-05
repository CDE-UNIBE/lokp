Ext.define('Lmkp.controller.moderation.CompareReview', {
    extend: 'Ext.app.Controller',

    stores: [
        'CompareInvolvements',
        'CompareTagGroups',
        'CompareVersions',
        'CompareMetadata',
        'ReviewDecisions'
    ],

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
            'lo_moderatorcomparereview gridpanel templatecolumn[itemId=compareGridReviewableColumn]': {
                afterrender: this.onCompareGridReviewableColumnAfterRender
            }
        });
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
            '<b>Version</b>: {0}<br/>' +
            '<b>Timestamp</b>: {1}<br/>' +
            '<b>User</b>: TODO'
        );
        var refPanel = this.getRefMetadataPanel();
        var newPanel = this.getNewMetadataPanel();
        if (refPanel && newPanel) {
            refPanel.update(template.apply([
                metaModelInstance.get('ref_version'),
                metaModelInstance.get('ref_timestamp')
            ]));
            newPanel.update(template.apply([
                metaModelInstance.get('new_version'),
                metaModelInstance.get('new_timestamp')
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
        var win = this.getCompareWindow();

        if (win) {
            win.setLoading(true);
        }

        var url = this._getUrl(action, type, uid, refVersion, newVersion);

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
                            'Information',
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

        if (form && version && identifier && type) {
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
                    return '<img src="/static/img/exclamation.png" style="cursor:pointer;" title="Involvement can not be reviewed. Click for more information.">';
                } else if (reviewable == -2) {
                    // Stakeholder has no active version
                    return '<img src="/static/img/exclamation.png" style="cursor:pointer;" title="Involvement can not be reviewed. Click for more information.">';
                } else if (reviewable > 0) {
                    // Involvement can be reviewed
                    return '<img src="/static/img/accept.png" title="Involvement can be reviewed">';
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
                if (record && record.get('reviewable') == -2) {
                    var data = record.get('new');
                    if (data && data.identifier) {
                        var win = Ext.create('Ext.window.Window', {
                            title: 'Review not possible',
                            bodyPadding: 10,
                            modal: true,
                            width: 300,
                            html: 'The Stakeholder of this involvement has no active version and cannot be set active. Please review the Stakeholder first.',
                            buttons: [
                                {
                                    text: 'OK',
                                    handler: function() {
                                        win.close();
                                    }
                                }, {
                                    text: 'Review Stakeholder',
                                    handler: function() {
                                        // Refresh the panel
                                        me.reloadCompareTagGroupStore(
                                            'review', 'stakeholders', data.identifier
                                        );
                                        win.close();
                                    }
                                }
                            ]
                        }).show();
                    }
                }
            });
        }
    },

    onCompareColumnAfterRender: function(comp) {
        comp.renderer = function(value, metaData, record) {
            if (value) {
                metaData.tdCls = value['class'];
                var html = "";
                for(var i = 0; i < value.tags.length; i++){
                    var tag = value.tags[i];
                    var prefix = "";
                    if(value['class'] == 'add' || value['class'] == 'add involvement'){
                        prefix += "+ ";
                    } else if(value['class'] == 'remove' || value['class'] == 'remove involvement'){
                        prefix += "- ";
                    }
                    html += "<div>" + prefix + tag.key + ": " + tag.value + "</div>";
                }
                if (value['class'] == 'add involvement'
                    || value['class'] == 'remove involvement') {
                    metaData.tdAttr = 'data-qtip="' + 'It is possible that not all attributes are shown here!' + '"';
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

        win.setLoading(true);
        win.setTitle('Compare');
        win.add({
            xtype: 'lo_moderatorcomparereview',
            action: 'compare'
        });

        var mData = this.getCompareMetadataStore().first();

        this.reloadCompareTagGroupStore(
            'compare',
            mData.get('type'),
            mData.get('identifier')
        );
    },

    onReviewButtonClick: function() {
    	
    	var me = this;

		// Special case: Stakeholders with pending involvement. These are 
		// normally hidden but can be accessed directly from the 'normal' 
		// interface by clicking the review button. If this is the case, show
		// message to guide the user to the activity side where the involvement
		// can be reviewed. 
		var invStore = this.getCompareInvolvementsStore();
		if (invStore) {
			var inv = invStore.first();
		}
		
		if (inv) {
			var newInv = inv.get('new');
			var identifier = newInv.identifier;
			var reviewable = inv.get('reviewable');
		}
		
        var mData = this.getCompareMetadataStore().first();
		var type = mData.get('type');
		
		if (reviewable == -2 && type == 'stakeholders' && identifier) {
			var msgWin = Ext.create('Ext.window.Window', {
                title: 'Review not possible',
                bodyPadding: 10,
                modal: true,
                width: 300,
                html: 'Involvements can only be reviewed through Activities. Please review the Activity to approve this involvement.',
                buttons: [
                    {
                        text: 'OK',
                        handler: function() {
                            msgWin.close();
                        }
                    }, {
                        text: 'Review Activity',
                        handler: function() {
                            // Refresh the panel
                            me.reloadCompareTagGroupStore(
                                'review', 'activities', identifier
                            );
                            msgWin.close();
                        }
                    }
                ]
            }).show();
		} else {
	        var win = this.getCompareWindow();
	        if (!win) {
	            win = this._createWindow();
	            win.show();
	        } else {
	            win.removeAll();
	        }
	
	        win.setLoading(true);
	        win.setTitle('Review');
	        win.add({
	            xtype: 'lo_moderatorcomparereview',
	            action: 'review'
	        });
	
	        this.reloadCompareTagGroupStore(
	            'review',
	            mData.get('type'),
	            mData.get('identifier')
	        );
		}
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

    _createWindow: function(title) {
        var win = Ext.create('Ext.window.Window', {
            name: 'compareWindow',
            title: title,
            layout: 'fit',
            border: false,
            height: 700,
            width: 700,
            modal: true
        });
        return win;
    },

    _getUrl: function(action, type, uid, refVersion, newVersion) {
        if (action && type && uid) {
            var url = '/' + type + '/' + action + '/json/' + uid;
            if (refVersion && newVersion) {
                url += '/' + refVersion + '/' + newVersion;
            } else if (!refVersion && newVersion) {
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