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
			}
		});
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
		console.log(Lmkp.ts.msg("locale"));
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
