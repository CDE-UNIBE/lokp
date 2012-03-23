Ext.define('Lmkp.controller.admin.Main', {
	extend: 'Ext.app.Controller',
	
	views: [
		'admin.MainPanel',
		'admin.Home'
	],
	
	refs: [{
		ref: 'mainPanel',
		selector: 'adminmainpanel'
	}],
	
	init: function() {
		this.control({
			'toolbar button[id=home]': {
				click: this.showHome
			},
			'toolbar menuitem[id=yaml_scan]': {
				click: this.showYamlScan
			}
		});
	},
	
	showHome: function(item, e, eOpts) {
		var newElement = Ext.create('Lmkp.view.admin.Home');
		this._replaceContent(newElement);
	},
	
	showYamlScan: function(item, e, eOpts) {
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
