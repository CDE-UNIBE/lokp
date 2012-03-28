Ext.define('Lmkp.controller.admin.Main', {
	extend: 'Ext.app.Controller',

	views: [
		'admin.MainPanel',
		'admin.Home',
		
		'admin.YamlScan'
	],
	
	stores: ['YamlScan'],
	
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
			}
		});
	},
	
	scanDoScan: function(item, e, eOpts) {
		var store = this.getYamlScanStore();
		var root = store.getRootNode();
		root.removeAll(false);
		store.load({
			node: root
		});
	},
	
	mainShowHome: function(item, e, eOpts) {
		var newElement = Ext.create('Lmkp.view.admin.Home');
		this._replaceContent(newElement);
	},
	
	mainShowYamlScan: function(item, e, eOpts) {
		var newElement = Ext.create('Lmkp.view.admin.YamlScan');
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
