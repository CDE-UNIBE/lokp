Ext.define('Lmkp.view.administrator.YamlScan', {
    extend: 'Ext.tree.Panel',

    alias: ['widget.lo_administratoryamlscanpanel'],
    
    border: 0,
    autoScroll: true,
    layout: 'fit',

    dockedItems: [
        {
            xtype: 'toolbar',
            defaults: {
                iconAlign: 'top',
                scale: 'medium'
            },
            items: [
                {
                    itemId: 'yaml-scan-button',
                    text: Lmkp.ts.msg('button_refresh'),
                    tooltip: Lmkp.ts.msg('tooltip_refresh'),
                    iconCls: 'button-refresh'
                }, {
                    itemId: 'yaml-add-button',
                    text: Lmkp.ts.msg('administration_add-all-to-database'),
                    iconCls: 'button-add'
                }, '->', {
                    xtype: 'combobox',
                    itemId: 'yamlScanProfileCombobox',
                    fieldLabel: Lmkp.ts.msg('gui_profile'),
                    labelAlign: 'right',
                    queryMode: 'local',
                    store: 'Profiles',
                    displayField: 'name',
                    valueField: 'profile',
                    value: Ext.util.Cookies.get('_PROFILE_') ? Ext.util.Cookies.get('_PROFILE_') : 'global',
                    margin: '0 10 0 0'
                }
            ]
        }
    ],

    rootVisible: false,
    columns: [{
        xtype: 'treecolumn',
        header: Lmkp.ts.msg('translation_original'),
        flex: 1,
        dataIndex: 'value',
        sortable: true
    },{
        xtype: 'templatecolumn',
        name: 'mandatory',
        text: Lmkp.ts.msg('translation_mandatory'),
        flex: 0,
        sortable: true,
        dataIndex: 'mandatory',
        align: 'center',
        tpl: ''
    }, {
        xtype: 'templatecolumn',
        name: 'local',
        text: Lmkp.ts.msg('translation_global-attribute'),
        flex: 0,
        sortable: true,
        dataIndex: 'local',
        align: 'center',
        tpl: ''
    }, {
        xtype: 'templatecolumn',
        name: 'exists',
        text: Lmkp.ts.msg('administration_is-in-database'),
        flex: 0,
        sortable: true,
        dataIndex: 'exists',
        align: 'center',
        tpl: ''
    }]
})
