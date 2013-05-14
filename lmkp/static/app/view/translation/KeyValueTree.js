Ext.define('Lmkp.view.translation.KeyValueTree', {
    extend: 'Ext.tree.Panel',

    alias: 'widget.lo_translationkeyvaluetree',

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
                    itemId: 'keyvalueRefreshButton',
                    text: Lmkp.ts.msg('button_refresh'),
                    tooltip: Lmkp.ts.msg('tooltip_refresh'),
                    iconCls: 'button-refresh'
                }, '->', {
                    xtype: 'combobox',
                    itemId: 'keyvalueProfileCombobox',
                    fieldLabel: Lmkp.ts.msg('gui_profile'),
                    labelAlign: 'right',
                    queryMode: 'local',
                    store: 'Profiles',
                    displayField: 'name',
                    valueField: 'profile',
                    value: Ext.util.Cookies.get('_PROFILE_') ? Ext.util.Cookies.get('_PROFILE_') : 'global'
                }, {
                    xtype: 'combobox',
                    itemId: 'keyvalueLanguageCombobox',
                    fieldLabel: Lmkp.ts.msg('gui_language'),
                    labelAlign: 'right',
                    queryMode: 'local',
                    store: 'Languages',
                    displayField: 'local_name',
                    valueField: 'locale',
                    value: Lmkp.ts.msg("locale"),
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
        header: Lmkp.ts.msg('translation_translation'),
        name: 'translation',
        flex: 1,
        dataIndex: 'translation',
        sortable: true,
        tpl: ''
    }, {
        xtype: 'templatecolumn',
        name: 'editColumn',
        width: 50,
        align: 'center',
        tpl: ''
    }]
});