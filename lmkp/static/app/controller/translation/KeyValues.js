Ext.define('Lmkp.controller.translation.KeyValues', {
    extend: 'Ext.app.Controller',

    init: function() {
        this.control({
            'lo_translationkeyvaluetree templatecolumn[name=mandatory]': {
                afterrender: this.onMandatoryColumnAfterrender
            },
            'lo_translationkeyvaluetree templatecolumn[name=local]': {
                afterrender: this.onLocalColumnAfterrender
            },
            'lo_translationkeyvaluetree templatecolumn[name=translation]': {
                afterrender: this.onTranslationColumnAfterrender
            },
            'lo_translationkeyvaluetree templatecolumn[name=editColumn]': {
                afterrender: this.onEditColumnAfterrender,
                click: this.onEditColumnClick
            },
            'lo_translationkeyvaluetree button[itemId=keyvalueRefreshButton]': {
                click: this.doKeyvalueRefresh
            },
            'lo_translationkeyvaluetree combobox[itemId=keyvalueProfileCombobox]': {
                select: this.doKeyvalueRefresh
            },
            'lo_translationkeyvaluetree combobox[itemId=keyvalueLanguageCombobox]': {
                select: this.doKeyvalueRefresh
            }
        });
    },

    /**
     * Nicely render the column showing whether a key/value is mandatory or not.
     * Also used by: controller.administrator.YamlScan
     * comp: grid cell
     */
    onMandatoryColumnAfterrender: function(comp) {
        comp.renderer = function(value) {
            if (value == true) {
                return '<b>' + Lmkp.ts.msg('button_yes') + '</b>';
            } else {
                return Lmkp.ts.msg('button_no');
            }
        }
    },

    /**
     * Nicely render the column showing whether a key/value is global or not.
     * Also used by: controller.administrator.YamlScan
     * comp: grid cell
     */
    onLocalColumnAfterrender: function(comp) {
        comp.renderer = function(value) {
            if (value == false) {
                return '<b>' + Lmkp.ts.msg('button_yes') + '</b>';
            } else {
                return Lmkp.ts.msg('button_no');
            }
        }
    },

    /**
     * Nicely render the column showing the translation.
     * comp: grid cell
     */
    onTranslationColumnAfterrender: function(comp) {
        comp.renderer = function(value) {
            if (value == 1) {
                // Not yet translated
                return '-';
            } else if (value == 0) {
                // Already in english
                return Lmkp.ts.msg('translation_original-already-in-english');
            } else {
                // Show translation
                return value;
            }
        }
    },

    /**
     * Nicely render the column to edit or add the translation.
     * comp: grid cell
     */
    onEditColumnAfterrender: function(comp) {
        comp.renderer = function(value, metaData, record) {
            if (record.get('exists')) {
                // Only show buttons if original is in database
                if (record.get('translation') == 1) {
                    // Not yet translated, show button to add new translation
                    return '<img src="static/img/application_form_add.png" title="' + Lmkp.ts.msg('translation_add-translation') + '" alt="' + Lmkp.ts.msg('translation_add-translation') + '"/>';
                } else if (record.get('translation') != 0) {
                    // If not in english, show button to edit translation
                    return '<img src="static/img/application_form_edit.png" title="' + Lmkp.ts.msg('translation_edit-translation') + '" alt="' + Lmkp.ts.msg('translation_edit-translation') + '"/>';
                }
            }
            return '';
        }
    },

    /**
     * Show a window to do the translation and handle the submit action.
     * g: the grid of the treepanel
     */
    onEditColumnClick: function(g) {
        var me = this;
        var record = g.getSelectionModel().getSelection()[0];
        var panel = g.up('panel');

        if (panel && record && record.get('translation') != 0 && record.get('exists')) {

            var oldTranslation;
            if (record.get('translation') != 1) {
                oldTranslation = record.get('translation');
            }

            var languageCb = panel.down('combobox[itemId=keyvalueLanguageCombobox]');
            var locale = languageCb && languageCb.getValue() ? languageCb.getValue() : 'en';

            var win = Ext.create('Ext.window.Window', {
                title: Lmkp.ts.msg('translation_translation'),
                layout: 'fit',
                border: false,
                modal: true,
                items: [
                    {
                        xtype: 'form',
                        url: '/lang/edit',
                        bodyPadding: 5,
                        defaults: {
                            anchor: '100%',
                            xtype: 'textfield'
                        },
                        items: [
                            {
                                xtype: 'displayfield',
                                fieldLabel: Lmkp.ts.msg('gui_language'),
                                value: Lmkp.ts.msg('locale_local-name')
                            }, {
                                xtype: 'displayfield',
                                fieldLabel: Lmkp.ts.msg('translation_key-or-value'),
                                value: record.get('value')
                            }, {
                                name: 'translation',
                                fieldLabel: Lmkp.ts.msg('translation_translation'),
                                value: oldTranslation,
                                allowBlank: false
                            }
                        ],
                        bbar: ['->',
                            {
                                text: Lmkp.ts.msg('button_submit'),
                                tooltip: Lmkp.ts.msg('tooltip_submit'),
                                iconCls: 'button-save',
                                iconAlign: 'top',
                                scale: 'medium',
                                handler: function() {
                                    var form = this.up('form').getForm();
                                    if (form.isValid()) {
                                        form.submit({
                                            // Add additional parameters to POST
                                            params: {
                                                'original': record.get('value'),
                                                'language': locale,
                                                'keyvalue': record.get('keyvalue'),
                                                'item_type': panel.type
                                            },
                                            waitMsg: Lmkp.ts.msg('gui_loading'),
                                            success: function(form, action) {
                                                // Reload the tree
                                                me.doKeyvalueRefresh(g);
                                                win.close();
                                                var w = Ext.create('Lmkp.utils.MessageBox');
                                                w.alert(
                                                    Lmkp.ts.msg('feedback_success'),
                                                    action.result.msg
                                                );
                                            },
                                            failure: function(form, action) {
                                                win.close();
                                                var w = Ext.create('Lmkp.utils.MessageBox');
                                                w.alert(
                                                    Lmkp.ts.msg('feedback_failure'),
                                                    action.result.msg
                                                );
                                            }
                                        });
                                    }
                                }
                            }, {
                                text: Lmkp.ts.msg('button_cancel'),
                                tooltip: Lmkp.ts.msg('tooltip_cancel'),
                                iconCls: 'button-close',
                                iconAlign: 'top',
                                scale: 'medium',
                                handler: function() {
                                    this.up('form').getForm().reset();
                                    this.up('window').hide();
                                }
                            }
                        ]
                    }
                ]
            });
            win.show();
        }
    },

    /**
     * Do a refresh of the treepanel. Call may come from refresh button or
     * profile / language dropdown or after translation was added.
     * comp: button or combobox
     */
    doKeyvalueRefresh: function(comp) {

        var treepanel = comp.up('panel');
        treepanel.setLoading(true);

        var profileCb = treepanel.down('combobox[itemId=keyvalueProfileCombobox]');
        var profile = profileCb && profileCb.getValue() ? profileCb.getValue() : 'global';

        var languageCb = treepanel.down('combobox[itemId=keyvalueLanguageCombobox]');
        var locale = languageCb && languageCb.getValue() ? languageCb.getValue() : 'en';

        var store = treepanel.getStore();
        store.load({
            node: store.getRootNode(),
            params: {
                '_LOCALE_': locale,
                '_PROFILE_': profile
            },
            callback: function() {
                treepanel.setLoading(false);
            }
        });
    }
});