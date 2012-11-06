Ext.define('Lmkp.controller.administrator.YamlScan', {
    extend: 'Ext.app.Controller',

    views: [
    'administrator.CodeTab',
    'administrator.Main',
    'administrator.UserManagement',
    'administrator.YamlScan'
    ],
	
    stores: [
    'ActivityYamlScan',
    'StakeholderYamlScan',
    'Languages',
    'Profiles'
    ],
	
    refs: [{
        ref: 'mainPanel',
        selector: 'lo_administratormainpanel'
    }],
	
    init: function() {
        this.control({
            'lo_administratoryamlscanpanel templatecolumn[name=editColumn]': {
                click: this.showTranslationWindow
            },
            'lo_administratoryamlscanpanel toolbar button[itemId=yaml-scan-button]': {
                click: this.onScanButtonClick
            },
            'lo_administratoryamlscanpanel toolbar button[itemId=yaml-add-button]': {
                click: this.onAddButtonClick
            }
        });
    },

    showTranslationWindow: function(g, td) {
        var record = g.getSelectionModel().getSelection()[0];
        // only do some action if original is not in english (translation != 0)
        // and only if original is in database
        if (record.get('translation') != 0 && record.get('exists')) {

            // Save some values to refresh grid after submitting translation
            var controller = this;
            var panel = g.up('panel');
            if (panel) {
                var button = panel.down('button[itemId=yaml-scan-button]');
            }

            // Activity or Stakeholder?
            var item_type = null;
            if (panel.postUrl == '/config/add/activities') {
                item_type = 'activity';
            } else if (panel.postUrl == '/config/add/stakeholders') {
                item_type = 'stakeholder';
            }

            var win = Ext.create('Ext.window.Window', {
                title: 'Translation',
                layout: 'fit',
                modal: true,
                items: [{
                    xtype: 'form',
                    url: '/lang/edit',
                    defaults: {
                        anchor: '100%',
                        xtype: 'textfield'
                    },
                    items: [{
                        xtype: 'displayfield',
                        fieldLabel: 'Language',
                        value: Lmkp.ts.msg('locale_english-name')
                    }, {
                        xtype: 'displayfield',
                        fieldLabel: 'Key/Value',
                        value: record.get('value')
                    }, {
                        name: 'translation',
                        fieldLabel: 'Translation',
                        listeners: {
                            render: function() {
                                // show current translation value if not 1 (= not yet set)
                                if (record.get('translation') != 1) {
                                    this.setValue(record.get('translation'));
                                }
                            }
                        },
                        allowBlank: false
                    }, {
                        name: 'original',
                        hidden: true,
                        value: record.get('value'),
                        allowBlank: false
                    }, {
                        name: 'language',
                        hidden: true,
                        value: Lmkp.ts.msg('locale'),
                        allowBlank: false
                    }, {
                        name: 'keyvalue',
                        hidden: true,
                        value: record.get('keyvalue'),
                        allowBlank: false
                    }, {
                        name: 'item_type',
                        hidden: true,
                        value: item_type,
                        allowBlank: false
                    }],
                    buttons: [{
                        text: 'Save',
                        handler: function() {
                            if (this.up('form').getForm().isValid()) {
                                this.up('form').getForm().submit({
                                    waitMsg: 'Sending ...',
                                    success: function(form, action) {
                                        win.close();
                                        Ext.Msg.alert('Success', action.result.msg);
                                        // Reload grid
                                        if (button) {
                                            controller.onScanButtonClick(button);
                                        }
                                    },
                                    failure: function(form, action) {
                                        Ext.Msg.alert('Failure', action.result.msg);
                                    }
                                });
                            }
                        }
                    }, {
                        text: 'Cancel',
                        handler: function() {
                            this.up('form').getForm().reset();
                            this.up('window').hide();
                        }
                    }]
                }]
            });
            win.show();
        }
    },
	
    onAddButtonClick: function(button, event, eOpts) {
        // The profile combobox
        var cbProfile = Ext.ComponentQuery.query('combobox[id=profile_combobox]')[0];
        // The parent YamlScanPanel
        var panel = button.ownerCt.ownerCt;
        
        var win = Ext.create('Ext.window.Window', {
            title: 'Add to DB',
            closable: true,
            layout: 'fit',
            height: 300,
            width: 400,
            autoScroll: true,
            loader: {
                url: panel.getPostUrl(),
                params: {
                    '_PROFILE_': cbProfile.lastSelection[0].get('profile')
                },
                loadMask: true,
                autoLoad: true
            },
            buttons: [{
                text: 'OK',
                handler: function() {
                    this.up('window').hide();
                }
            }]
        });
        win.on('hide', function(component, eOpts){
            this.onScanButtonClick(button);
        }, this);
        win.show();
    },
	
    onScanButtonClick: function(button, event, eOpts){
        // The comboboxes with language and profile
        var cbLang = Ext.ComponentQuery.query('combobox[id=language_combobox]')[0];
        var cbProfile = Ext.ComponentQuery.query('combobox[id=profile_combobox]')[0];

        // Then get the treepanel and its store
        var treepanel = button.up('panel');
        var store = treepanel.getStore();
        var root = store.getRootNode();
        // catch error when no language is in db yet
        var lang = (cbLang.lastSelection[0]) ? cbLang.lastSelection[0].get('locale') : 'en';
        root.removeAll(false);
        store.load({
            node: root,
            params: {
                '_LOCALE_': lang,
                '_PROFILE_': cbProfile.lastSelection[0].get('profile')
            }
        });
        // try to reload Language store to populate combobox
        // this should only take place after first language (english) was inserted into DB,
        // which usually takes place on first add of key/value pairs.
        if (!cbLang.lastSelection[0]) {
            cbLang.getStore().load({
                scope: this,
                callback: function(records, operation, success) {
                    if (records.length == 1) {
                        cbLang.setValue(records[0].get('locale'));
                    }
                }
            });
        }
    }
    
});
