Ext.define('Lmkp.controller.admin.Main', {
	extend: 'Ext.app.Controller',

	views: [
		'admin.MainPanel',
		'admin.Home',
		'admin.YamlScan'
	],
	
	stores: [
		'YamlScan',
		'Languages',
		'Profiles'
	],
	
	refs: [{
		ref: 'mainPanel',
		selector: 'adminmainpanel'
	}],
	
	init: function() {
		this.control({
			'toolbar[id=scanToolbar] button[id=scanButton]': {
				click: this.scanDoScan
			},
			'toolbar[id=scanToolbar] button[id=addToDB]': {
				click: this.scanAddToDB
			},
			'toolbar[id=scanToolbar] combobox[id=scanLanguageCombo]': {
				select: this.scanDoScan
			},
			'toolbar[id=scanToolbar] combobox[id=scanProfileCombo]': {
				select: this.scanDoScan
			},
			'adminyamlscan': {
				beforerender: this.renderAdminYamlScan
			},
			'adminyamlscan templatecolumn[name=editColumn]': {
				click: this.showTranslationWindow
			}
		});
	},
	
	showTranslationWindow: function(g, td) {
		var record = g.getSelectionModel().getSelection()[0];
		// only do some action if original is not in english (translation != 0)
		// and only if original is in database
		if (record.get('translation') != 0 && record.get('exists')) {
			var panel = this;
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
						value: Ext.ComponentQuery.query('combobox[id=scanLanguageCombo]')[0].lastSelection[0].get('english_name')
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
						value: Ext.ComponentQuery.query('combobox[id=scanLanguageCombo]')[0].lastSelection[0].get('locale'),
						allowBlank: false
					}, {
						name: 'keyvalue',
						hidden: true,
						value: record.get('keyvalue'),
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
										panel.scanDoScan();
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
	
	scanAddToDB: function(item, e, eOpts) {
		var cbProfile = Ext.ComponentQuery.query('combobox[id=scanProfileCombo]')[0];
		var win = Ext.create('Ext.window.Window', {
			title: 'Add to DB',
			closable: false,
			layout: 'fit',
			loader: {
				url: '/config/add',
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
		win.on('hide', this.scanDoScan, this);
		win.show();
	},
	
	scanDoScan: function(item, e, eOpts) {
		var cbLang = Ext.ComponentQuery.query('combobox[id=scanLanguageCombo]')[0];
		var cbProfile = Ext.ComponentQuery.query('combobox[id=scanProfileCombo]')[0];
		var store = this.getYamlScanStore();
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
	},
	
	renderAdminYamlScan: function() {
		this.getLanguagesStore().load();
		var cb1 = Ext.ComponentQuery.query('combobox[id=scanLanguageCombo]')[0];
		cb1.setValue(Lmkp.ts.msg("locale"));
		this.getProfilesStore().load();
		var initialProfile = 'global';
		var cb2 = Ext.ComponentQuery.query('combobox[id=scanProfileCombo]')[0];
		cb2.setValue(initialProfile);
	}
});
