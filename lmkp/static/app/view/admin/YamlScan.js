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
			xtype: 'templatecolumn',
			name: 'mandatory',
            text: 'Mandatory',
            flex: 1,
            sortable: true,
            dataIndex: 'mandatory',
            align: 'center',
            tpl: Ext.create('Ext.XTemplate', '{[this.isInDB(values.mandatory)]}', {
            	isInDB: function(m) {
            		if (m) {
            			return 'yes';
            		} else {
            			return '<i>no</i>';
            		}
            	}
            })
		}, {
			xtype: 'templatecolumn',
            text: 'In DB',
            flex: 1,
            sortable: true,
            dataIndex: 'exists',
            align: 'center',
            tpl: Ext.create('Ext.XTemplate', '{[this.isInDB(values.exists)]}', {
            	isInDB: function(e) {
            		if (e) {
            			return 'yes';
            		} else {
            			return '<b>no</b>';
            		}
            	}
            })
		}, {
			header: 'Translation',
			flex: 1,
			dataIndex: 'translation',
			sortable: true,
			align: 'center'
		}],
		dockedItems: [{
			xtype: 'toolbar',
			dock: 'bottom',
			id: 'scanToolbar',
			items: [{
				text: 'Scan',
				id: 'scanButton'
			}, {
				text: 'Add all to DB',
				id: 'addToDB'
			}]
		}]
	}],
	
	initComponent: function() {
		this.callParent(arguments);
	}
})
