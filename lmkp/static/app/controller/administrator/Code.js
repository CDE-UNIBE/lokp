Ext.define('Lmkp.controller.administrator.Code', {
    extend: 'Ext.app.Controller',

    views: [
        'administrator.CodeTab'
    ],

    init: function() {
        this.control({
            'lo_administratorcodetab button[itemId=code_file_scan]': {
                click: this.onFileScanButtonClick
            },
            'lo_administratorcodetab combobox[itemId=code_file_combobox]': {
                select: this.onFileComboboxSelect
            },
            'lo_administratorcodetab button[itemId=code_submit_button]': {
                click: this.onCodeSubmitButtonClick
            }
        });
    },

    onFileScanButtonClick: function(button) {
        // Define a temporary model
        Ext.define('File', {
            extend: 'Ext.data.Model',
            fields: [
                {
                    name: 'filename',
                    type: 'string'
                }, {
                    name: 'description',
                    type: 'string'
                }, {
                    name: 'delimiter',
                    type: 'string'
                }, {
                    name: 'success',
                    type: 'boolean'
                }, {
                    name: 'item',
                    type: 'string'
                }
            ]
        });
        // Create a store
        var store = Ext.create('Ext.data.Store', {
            model: 'File',
            proxy: {
                type: 'ajax',
                url: '/codes/files',
                reader: {
                    type: 'json',
                    root: 'files'
                }
            }
        });
        // Find combobox
        var panel = button.up('panel');
        var combobox = panel.query('combobox[itemId=code_file_combobox]')[0];
        // Load the store and bind it to combobox
        store.load(function(records) {
            combobox.bindStore(store);
        });
    },

    onFileComboboxSelect: function(combobox, records) {
        var file = records[0];
        // Populate settings
        var description = Ext.ComponentQuery.query('textfield[itemId=description]')[0];
        if (description) {
            description.setValue(file.get('description'));
        }
        var delimiter = Ext.ComponentQuery.query('textfield[itemId=delimiter]')[0];
        if (delimiter) {
            delimiter.setValue(file.get('delimiter'));
        }
        var value_type = Ext.ComponentQuery.query('combobox[itemId=value_type]')[0];
        if (value_type) {
            value_type.setValue(file.get('item'));
        }
    },

    onCodeSubmitButtonClick: function(button) {
        var me = this;
        var form = button.up('form').getForm();
        if (form.isValid()) {
            form.submit({
                success: function(form, action) {
                    var res = Ext.JSON.decode(action.response.responseText);
                    me._showFeedback(res);
                },
                failure: function(form, action) {
                    var res = Ext.JSON.decode(action.response.responseText);
                    me._showFeedback(res);
                }
            });
        }
    },

    _showFeedback: function(o) {
        // Textfield
        var msg = [];
        for (var i in o.messages) {
            if (o.messages[i].success == false) {
                msg.push('<span class="red">' + o.messages[i].msg + '</span>');
            } else {
                msg.push(o.messages[i].msg);
            }
        }
        var textfield = Ext.ComponentQuery.query('textarea[itemId=feedback_textarea]')[0];
        if (textfield) {
            textfield.setValue(msg.join('\n'));
        }

        // Statusbar
        var statusbar = Ext.ComponentQuery.query('panel[itemId=code_statusbar]')[0];
        var success = o.success ? '<span class="green">Success</span>' : '<span class="red">Error</span>'
        if (o.insertCount != null && o.errorCount != null) {
            statusbar.update('Status: ' + success + ' (' + o.insertCount + ' codes inserted, ' + o.errorCount + ' errors encountered)');
        } else {
            statusbar.update('Status: ' + success + ' (' + o.msg + ')');
        }
    }
});