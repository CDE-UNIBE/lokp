Ext.define('Lmkp.view.admin.MainPanel', {
	extend: 'Ext.tab.Panel',
	
	alias: ['widget.adminmainpanel'],
	
	// tbar: [{
		// text: 'Home',
		// xtype: 'button',
		// id: 'home'
	// }, {
		// text: 'YAML',
		// xtype: 'button',
		// menu: {
			// xtype: 'menu',
			// items: [{
				// text: 'Scan',
				// id: 'yaml_scan'
			// }]
		// }
	// }],
	
	activeTab: 0,
	
	items: [{
		title: 'Home',
		xtype: 'adminhome'
		// xtype: 'adminyamlscan'
	}, {
		title: 'YAML',
		xtype: 'adminyamlscan'
	}],
	
	initComponent: function() {
		this.callParent(arguments);
	}
});