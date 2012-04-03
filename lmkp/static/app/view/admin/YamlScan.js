Ext.define('Lmkp.view.admin.YamlScan', {
	extend: 'Ext.panel.Panel',
	
	alias: ['widget.adminyamlscan'],

	border: 0,
	
	items: [{
		xtype: 'treepanel',
		store: 'YamlScan',
		rootVisible: false,
		height: 500,
		columns: [{
			xtype: 'treecolumn',
			header: 'Original',
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
            tpl: Ext.create('Ext.XTemplate', '{[this.isMandatory(values.mandatory)]}', {
            	isMandatory: function(m) {
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
			xtype: 'templatecolumn',
			header: 'Translation',
			flex: 1,
			dataIndex: 'translation',
			sortable: true,
			tpl: Ext.create('Ext.XTemplate', '{[this.showTranslation(values.translation)]}', {
				showTranslation: function(t) {
					if (t == 1) {			// not yet translated
						return '-';
					} else if (t == 0) {	// already in english
						return '[already translated]';
					} else {				// show translation
						return t;
					}
				}
			})
		}, {
			xtype: 'templatecolumn',
			name: 'editColumn',
			width: 25,
			align: 'center',
			tpl: Ext.create('Ext.XTemplate', '{[this.showTranslationButton(values.exists, values.translation)]}', {
				showTranslationButton: function(e, t) {
					if (e) {		// only show buttons when original in database
						if (t == 1) {			// not yet translated
							return '<img src="static/img/application_form_add.png" title="add translation" alt="add translation"/>';
						} else if (t == 0) {	// already in english
							return '';
						} else {				// show translation
							return '<img src="static/img/application_form_edit.png" title="edit translation" alt="edit translation"/>';
						}
					} else {
						return '';
					}
				}
			})
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
			}, '->', 
			'Scan profile:',
			{
				xtype: 'combobox',
				id: 'scanProfileCombo',
				queryMode: 'local',
				store: 'Profiles',
				displayField: 'name',
				valueField: 'profile',
				forceSelection: true
			},
			'Scan language:',
			{
				xtype: 'combobox',
				id: 'scanLanguageCombo',
				queryMode: 'local',
				store: 'Languages',
				displayField: 'english_name',
				valueField: 'locale',
				forceSelection: true
			}]
		}]
	}],
	
	initComponent: function() {
		this.callParent(arguments);
	}
})
