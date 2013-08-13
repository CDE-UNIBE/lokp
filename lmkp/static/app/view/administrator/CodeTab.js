Ext.define('Lmkp.view.administrator.CodeTab', {
    extend: 'Ext.panel.Panel',
    alias: ['widget.lo_administratorcodetab'],

    layout: 'border',
    defaults: {
        bodyPadding: 5
    },

    items: [{
        xtype: 'form',
        url: 'translation/batch',
        region: 'north',
        layout: 'column',
        items: [
        {
            xtype: 'fieldset',
            title: 'Input',
            columnWidth: 1/2,
            margin: '0 5 0 0',
            defaults: {
                bodyPadding: 5,
                layout: 'anchor'
            },
            items: [
            {
                xtype: 'panel',
                layout: 'hbox',
                border: 0,
                anchor: '100%',
                items: [
                {
                    xtype: 'combobox',
                    fieldLabel: 'File',
                    itemId: 'code_file_combobox',
                    displayField: 'filename',
                    valueField: 'filename',
                    name: 'filename',
                    queryMode: 'local',
                    flex: 1
                }, {
                    xtype: 'button',
                    itemId: 'code_file_scan',
                    text: 'scan',
                    flex: 0
                }
                ]
            }, {
                xtype: 'component',
                html: 'or',
                margin: '0 0 5 0'
            }, {
                xtype: 'textarea',
                fieldLabel: 'Text',
                name: 'code_text',
                emptyText: '{translation} {delimiter} {value} [{delimiter} {helptext_original} {delimiter} {helptext_translation}] (Not yet supported)',
                anchor: '100%'
            }
            ]
        }, {
            xtype: 'panel',
            border: 0,
            columnWidth: 1/2,
            items: [
            {
                xtype: 'fieldset',
                title: 'Settings',
                defaults: {
                    layout: 'anchor'
                },
                items: [
                {
                    xtype: 'textfield',
                    fieldLabel: 'Description',
                    itemId: 'description',
                    anchor: '100%'
                }, {
                    xtype: 'textfield',
                    fieldLabel: 'Delimiter',
                    itemId: 'delimiter',
                    name: 'delimiter',
                    anchor: '100%',
                    allowBlank: false
                }, {
                    xtype: 'combobox',
                    fieldLabel: 'Value type',
                    store: [
                        'A_Key',
                        'A_Value',
                        'SH_Key',
                        'SH_Value',
                        'Category'
                    ],
                    itemId: 'value_type',
                    name: 'item_type',
                    anchor: '100%',
                    allowBlank: false
                }, {
                    xtype: 'combobox',
                    fieldLabel: 'Language',
                    store: 'Languages',
                    displayField: 'local_name',
                    valueField: 'locale',
                    forceSelection: true,
                    editable: false,
                    itemId: 'language_cb',
                    name: 'locale',
                    anchor: '100%'
                }
                ]
            }, {
                xtype: 'panel',
                border: 0,
                layout: 'hbox',
                items: [
                {
                    xtype: 'component',
                    flex: 1
                }, {
                    xtype: 'button',
                    formBind: true,
                    disabled: true,
                    text: 'Go',
                    flex: 0,
                    itemId: 'code_submit_button'
                }
                ]

            }
            ]
        }
        ]
    }, {
        xtype: 'textarea',
        itemId: 'feedback_textarea',
        region: 'center',
        readOnly: true,
        margin: 5
    }
    ],
    bbar: [{
        xtype: 'panel',
        itemId: 'code_statusbar',
        html: 'Status: Ready',
        frame: false,
        border: false,
        bodyStyle: 'background:transparent;'
    }]
});