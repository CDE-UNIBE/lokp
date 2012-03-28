Ext.define('Lmkp.view.admin.MainPanel', {
	extend: 'Ext.panel.Panel',
	
	alias: ['widget.adminmainpanel'],
	
	tbar: [{
		text: 'Home',
		xtype: 'button',
		id: 'home'
	}, {
		text: 'YAML',
		xtype: 'button',
		menu: {
			xtype: 'menu',
			items: [{
				text: 'Scan',
				id: 'yaml_scan'
			}]
		}
	}],
	
	items: [{
		// xtype: 'adminhome'
		xtype: 'adminyamlscan'
	}],
	
	initComponent: function() {
		this.callParent(arguments);
	}
});