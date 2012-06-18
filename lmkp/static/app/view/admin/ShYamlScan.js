Ext.define('Lmkp.view.admin.ShYamlScan', {
    extend: 'Ext.panel.Panel',

    alias: ['widget.shadminyamlscan'],

    border: 0,
    layout: 'fit',

    items: [{
        xtype: 'treepanel',
        store: 'ShYamlScan',
        rootVisible: false,
        // TODO: autoScroll not yet working properly. Although scroll bar appears, it does so too late.
        autoScroll: true,
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
            name: 'local',
            text: 'Local YAML',
            flex: 1,
            sortable: true,
            dataIndex: 'local',
            align: 'center',
            tpl: Ext.create('Ext.XTemplate', '{[this.isLocal(values.local)]}', {
                isLocal: function(l) {
                    if (l) {
                        return 'yes';
                    } else {
                        return 'no';
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
            id: 'shScanToolbar',
            items: [{
                id: 'shScanButton',
                text: 'Scan'
            }, {
                id: 'shAddAllButton',
                text: 'Add all to DB'
            }],
            xtype: 'toolbar'
        }]
    }],

    initComponent: function() {
        this.callParent(arguments);
    }
})
