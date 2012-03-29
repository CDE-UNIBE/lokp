Ext.define('Lmkp.controller.admin.Main', {
	extend: 'Ext.app.Controller',

	views: [
		'admin.MainPanel',
		'admin.Home',
		
		'admin.YamlScan'
	],
	
	stores: [
		'YamlScan',
		'Languages'
	],
	
	refs: [{
		ref: 'mainPanel',
		selector: 'adminmainpanel'
	}],
	
	init: function() {
		this.control({
			'adminmainpanel toolbar button[id=home]': {
				click: this.mainShowHome
			},
			'adminmainpanel toolbar menuitem[id=yaml_scan]': {
				click: this.mainShowYamlScan
			},
			'toolbar[id=scanToolbar] button[id=scanButton]': {
				click: this.scanDoScan
			},
			'toolbar[id=scanToolbar] button[id=addToDB]': {
				click: this.scanAddToDB
			},
			'toolbar[id=scanToolbar] combobox[id=scanLanguageCombo]': {
				select: this.scanDoScan
			},
			'adminyamlscan templatecolumn[name=editColumn]': {
				click: this.showTranslationWindow
			}
		});
	},
	
	showTranslationWindow: function(g, td) {
		var record = g.getSelectionModel().getSelection()[0];
		// only do some action if original is not in english (translation != 0)
		if (record.get('translation') != 0) {
			console.log(record);
			var win = Ext.create('Ext.window.Window', {
				title: 'Translation',
				layout: 'fit',
				modal: true,
				items: [{
					xtype: 'form',
					url: '/lang/edit',
					defaults: {
						anchor: '100%'
					},
					items: [{
						xtype: 'displayfield',
						name: 'language',
						fieldLabel: 'Language',
						value: Ext.ComponentQuery.query('combobox[id=scanLanguageCombo]')[0].lastSelection[0].get('english_name')
					}, {
						xtype: 'displayfield',
						name: 'keyvalue',
						fieldLabel: 'Key/Value',
						value: record.get('value')
					}, {
						xtype: 'textfield',
						name: 'translation',
						fieldLabel: 'Translation',
						allowBlank: false
					}],
					buttons: [{
						text: 'Save',
						handler: function() {
							if (this.up('form').getForm().isValid()) {
								this.up('form').getForm().submit({
									success: function(form, action) {
										console.log("success");
									},
									failure: function(form, action) {
										console.log("failure");
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
	
	scanSwitchLanguage: function(combobox, records, eOpts) {
		// console.log(records[0].get('locale'));
		var store = this.getYamlScanStore();
		var root = store.getRootNode();
		root.removeAll(false);
		store.load({
			node: root,
			params: {
				'_LOCALE_': records[0].get('locale')
			}
		});
		console.log("don't delete me if you read this!!!");
		/*
		 * 
		 * 
		 * 
		 * 
		 * 
		 * 
		 * 
		 * 
		 * 
		 * 
		 * 
		 * 
		 */
	},
	
	scanAddToDB: function(item, e, eOpts) {
		var win = Ext.create('Ext.window.Window', {
			title: 'Add to DB',
			closable: false,
			layout: 'fit',
			loader: {
				url: '/config/add',
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
		var cb = Ext.ComponentQuery.query('combobox[id=scanLanguageCombo]')[0];
		var store = this.getYamlScanStore();
		var root = store.getRootNode();
		root.removeAll(false);
		if (cb.lastSelection[0]) {
			store.load({
				node: root,
				params: {
					'_LOCALE_': cb.lastSelection[0].get('locale')
				}
			});
		} else {
			store.load({
				node: root
			});
		}
	},
	
	mainShowHome: function(item, e, eOpts) {
		var newElement = Ext.create('Lmkp.view.admin.Home');
		this._replaceContent(newElement);
	},
	
	mainShowYamlScan: function(item, e, eOpts) {
		this.getLanguagesStore().load();
		var newElement = Ext.create('Lmkp.view.admin.YamlScan');
		var cb = Ext.ComponentQuery.query('combobox[id=scanLanguageCombo]')[0];
		cb.setValue(Lmkp.ts.msg("locale"));
		this._replaceContent(newElement);
	},
	
	_replaceContent: function(newElement) {
		var mainPanel = this.getMainPanel();
		if (mainPanel && mainPanel.items.first()) {
			if (mainPanel.items.first() != newElement) {
				mainPanel.remove(mainPanel.items.first());
				mainPanel.add(newElement);
			}
		}
	}
});
