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
        this.getRefMetadataPanel().update(template.apply([
            metaModelInstance.get('ref_version'),
            metaModelInstance.get('ref_timestamp')
        ]));
        this.getNewMetadataPanel().update(template.apply([
            metaModelInstance.get('new_version'),
            metaModelInstance.get('new_timestamp')
        ]));

        if (metaModelInstance.get('recalculated')
            && this.getComparePanel().action == 'review') {
            this.getRecalculationNotice().setVisible(true);
        } else {
            this.getRecalculationNotice().setVisible(false);
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
                url: type + '/review',
                params: {
                    version: version,
                    identifier: identifier
                },
                success: function(form, action) {
                    var result = Ext.JSON.decode(action.response.responseText);
                    infoWindow.alert(
                        Lmkp.ts.msg('feedback_success'),
                        result.msg
                    );
                    // Refresh the panel
                    me.reloadCompareTagGroupStore(
                        'review', type, identifier
                    );
                    // Also clear review comment
                    me.getReviewCommentTextarea().reset();
                    // TODO: Also refresh the list with pending versions
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

    onCompareColumnAfterRender: function(comp) {
        var me = this;
        comp.renderer = function(value, metaData, record) {

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

            if (me.getComparePanel() && me.getComparePanel().action == 'review') {
                if ((value['class'] == 'add involvement'
                        || value['class'] == 'remove involvement')
                    && (value.reviewable != 0)) {
                    if (value.reviewable == 1) {
                        console.log("reviewable == 1");
                        html += '<div>Reviewable: Item is brandnew and will be created.</div>';
                    } else if (value.reviewable == 2) {
                        console.log("reviewable == 2");
                        html += '<div>Reviewable: Item is based on an active version.</div>';
                    } else if (value.reviewable == 3) {
                        console.log("reviewable == 3");
                        html += '<div>Reviewable: Item is not based on an active version -> recalculation needed.</div>';
                    }
                } else if (value.reviewable == 0) {
                    console.log("not reviewable");
                    html += '<div>Not Reviewable: Item cannot be reviewed from here.</div>';
                }
            }
            return html;
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

        var mData = this.getCompareMetadataStore().first();

        this.reloadCompareTagGroupStore(
            'review',
            mData.get('type'),
            mData.get('identifier')
        );

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
            var url = type + '/' + action + '/json/' + uid;
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