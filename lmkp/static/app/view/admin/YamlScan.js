Ext.define('Lmkp.view.admin.YamlScan', {
	extend: 'Ext.panel.Panel',
	
	alias: ['widget.adminyamlscan'],
	
	html: 'This is where the YAML Scan magic will happen.',
	border: 0,
	
	items: [{
		xtype: 'treepanel',
		store: 'YamlScan',
		rootVisible: false,
		height: 400,
		width: '100%',
		columns: [{
			xtype: 'treecolumn',
			header: 'Name',
			flex: 1,
			dataIndex: 'value',
			sortable: true
		}, {
			header: 'Name2',
			flex: 1,
			dataIndex: 'translation',
			sortable: true
		// }, {
			// xtype: 'templatecolumn',
            // text: 'Duration',
            // flex: 1,
            // sortable: true,
            // dataIndex: 'translation',
            // align: 'center',
            // //add in the custom tpl for the rows
            // tpl: Ext.create('Ext.XTemplate', '{translation:this.testFunction}', {
                // testFunction: function(v) {
                	// var c = "bla" + v;
                    // return c;
                // }
            // })
		}]
	}],
	
	initComponent: function() {
		this.callParent(arguments);
	}
})
