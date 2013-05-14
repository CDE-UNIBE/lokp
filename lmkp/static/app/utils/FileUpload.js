Ext.define('Lmkp.utils.FileUpload', {
    extend: 'Ext.container.Container',

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    initComponent: function() {
        var me = this;
        this.items = [
            {
                xtype: 'panel',
                border: 0,
                layout: {
                    type: 'hbox'
                },
                items: [
                    {
                        xtype: 'container',
                        flex: 1
                    }, {
                        xtype: 'container',
                        items: [
                            {
                                xtype: 'button',
                                iconCls: 'button-add-file',
                                tooltip: Lmkp.ts.msg('tooltip_upload-new-file'),
                                handler: function() {
                                    var win = me.createUploadWindow();
                                    win.show();
                                }
                            }
                        ]
                    }
                ]
            }
        ];
        this.callParent(arguments);
    },

    /**
     * Custom function to set a predefined value. This adds all preexisting
     * files (in comma-separated string) to the panel.
     */
    setValue: function(value) {
        var values = value.split(',');
        for (var v in values) {
            var cv = values[v].split('|');
            if (cv.length == 2) {
                this.addSingleFilePanel(cv[0], cv[1]);
            }
        }
    },

    /**
     * Custom function to return the submit value when putting together the
     * form.
     */
    getSubmitValue: function() {
        // First, collect all values as objects in an array
        var fileObjects = [];
        var filepanels = this.query('panel[name=filepanelwithcontent]');
        for (var fp in filepanels) {
            var filenamefield = filepanels[fp].down('textfield[name=filepanel_filename]');
            var filename = filenamefield ? filenamefield.getSubmitValue() : null;
            if (filename != null) {
                fileObjects.push({
                    name: filename,
                    identifier: filepanels[fp].fileIdentifier
                });
            }
        }

        // Sort the objects by identifier
        fileObjects.sort(this._sort_by(
            'identifier', false, function(a){return a.toUpperCase()})
        );

        // Form an array-string out of the objects
        var ret = [];
        for (var i in fileObjects) {
            ret.push(fileObjects[i].name + '|' + fileObjects[i].identifier);
        }

        return ret.join(',');
    },

    /**
     * Function to add a single file panel with an existing file
     */
    addSingleFilePanel: function(fileName, fileIdentifier) {
        var me = this;
        me.insert(0, {
            xtype: 'panel',
            name: 'filepanelwithcontent',
            // Store the values to the top panel as well to make them accessible
            // more easily
            fileIdentifier: fileIdentifier,
            border: 0,
            layout: {
                type: 'hbox'
            },
            items: [
                {
                    xtype: 'textfield',
                    flex: 1,
                    value: fileName,
                    name: 'filepanel_filename'
                }, {
                    xtype: 'container',
                    defaults: {
                        margin: '0 0 2 2'
                    },
                    items: [
                        {
                            xtype: 'button',
                            iconCls: 'button-view-file',
                            tooltip: Lmkp.ts.msg('tooltip_view-file'),
                            handler: function() {
                                var fp = this.up('panel[name=filepanelwithcontent]');
                                if (fp && fp.fileIdentifier) {
                                    var url = '/files/view/' + fp.fileIdentifier;
                                    window.open(url, 'lo_fileview');
                                }
                            }
                        }, {
                            xtype: 'button',
                            iconCls: 'button-download-file',
                            tooltip: Lmkp.ts.msg('tooltip_download-file'),
                            handler: function() {
                                var fp = this.up('panel[name=filepanelwithcontent]');
                                if (fp && fp.fileIdentifier) {
                                    var url = '/files/download/' + fp.fileIdentifier;
                                    window.open(url, 'lo_fileview');
                                }
                            }
                        }, {
                            xtype: 'button',
                            iconCls: 'button-delete-file',
                            tooltip: Lmkp.ts.msg('tooltip_delete-file'),
                            fileName: fileName,
                            handler: function() {
                                var fp = this.up('panel[name=filepanelwithcontent]');
                                var filenamefield = fp.down('textfield[name=filepanel_filename]');
                                var filename = filenamefield ? filenamefield.getSubmitValue() : null;
                                if (fp && fp.fileIdentifier && filename) {
                                    Ext.create('Lmkp.utils.MessageBox').confirm(
                                        Lmkp.ts.msg('gui_please-confirm'),
                                        Lmkp.ts.msg('files_confirm-delete')
                                            .replace('{0}', '<b>'+filename+'</b>'),
                                        function(btn) {
                                            if (btn === 'yes') {
                                                me.removeSingleFilePanel(fp.fileIdentifier);
                                            }
                                        }
                                    );
                                }
                            }
                        }
                    ]
                }
            ]
        });
    },

    /**
     * Function to remove a file panel.
     */
    removeSingleFilePanel: function(fileIdentifier) {
        var filepanel = this._getFilePanelByIdentifier(fileIdentifier);
        if (filepanel) {
            this.remove(filepanel);
        }
    },

    /**
     * Show a window to upload a new file.
     */
    createUploadWindow: function() {
        
        var file_extensions = Lmkp.ts.msg('files_valid-extensions-list');

        // Prepare a regex expression to check for valid files on client side
        // based on file extensions
        var regexarray = [];
        for (var i in file_extensions) {
            regexarray[i] = '(\.' + file_extensions[i] + ')';
        }
        var file_extension_regex = new RegExp(
            '(.)+(' + regexarray.join("|") + ')$', "i");

        // Use the same extensions to show to the user as a hint (strip the
        // first character - the point)
        var extensions_hint = [];
        for (var j in file_extensions) {
            extensions_hint[j] = file_extensions[j].substring(1);
        }

        var me = this;
        var win = Ext.create('Ext.window.Window', {
            title: Lmkp.ts.msg('files_upload-new-file'),
            modal: true,
            layout: 'fit',
            items: [
                {
                    xtype: 'form',
                    bodyPadding: 10,
                    border: false,
                    modal: true,
                    defaults: {
                        anchor: '100%',
                        allowBlank: false
                    },
                    items: [
                        {
                            xtype: 'filefield',
                            emptyText: Lmkp.ts.msg('files_select-file'),
                            fieldLabel: Lmkp.ts.msg('files_file'),
                            name: 'file',
                            buttonText: Lmkp.ts.msg('button_browse'),
                            regex: file_extension_regex
                        }, {
                            xtype: 'panel',
                            data: {
                                fileExtensions: extensions_hint.join(', '),
                                maxFileSize: Lmkp.ts.msg('files_maximum-size')
                            },
                            border: 0,
                            tpl: Lmkp.ts.msg('files_maximum-file-size')
                                + ': {maxFileSize}<br/>'
                                + Lmkp.ts.msg('files_valid-extensions')
                                + ': {fileExtensions}'
                        }
                    ],
                    buttons: [
                        {
                            text: Lmkp.ts.msg('button_close'),
                            handler: function() {
                                win.close();
                            }
                        }, '->', {
                            text: Lmkp.ts.msg('button_upload'),
                            handler: function() {
                                var form = this.up('form').getForm();
                                if (form.isValid()) {
                                    form.submit({
                                        url: '/files/upload',
                                        waitMsg: Lmkp.ts.msg('files_uploading'),
                                        success: function(form, action) {
                                            var result = action.result;
                                            me.addSingleFilePanel(
                                                result.filename,
                                                result.fileidentifier
                                            );
                                            Ext.create('Lmkp.utils.MessageBox').alert(
                                                Lmkp.ts.msg('feedback_success'),
                                                result.msg
                                            );
                                            win.close();
                                        },
                                        failure: function(form, action) {
                                            var result = action.result;
                                            Ext.create('Lmkp.utils.MessageBox').alert(
                                                Lmkp.ts.msg('feedback_failure'),
                                                result.msg
                                            );
                                            win.close();
                                        }
                                    });
                                }
                            },
                            margin: 5
                        }
                    ]
                }
            ]
        });
        return win;
    },

    /**
     * Helper function to find a filepanel based on a fileidentifier.
     */
    _getFilePanelByIdentifier: function(fileIdentifier) {
        var filepanels = this.query('panel[name=filepanelwithcontent]');
        for (var fp in filepanels) {
            if (filepanels[fp].fileIdentifier == fileIdentifier) {
                return filepanels[fp];
            }
        }
        return null;
    },

    /**
     * Helper function to sort an array of json objects
     * http://stackoverflow.com/a/979325
     */
    _sort_by: function(field, reverse, primer){
        var key = function (x) {return primer ? primer(x[field]) : x[field]};
        return function (a,b) {
            var A = key(a), B = key(b);
            return (A < B ? -1 : (A > B ? 1 : 0)) * [1,-1][+!!reverse];
        }
    }
});