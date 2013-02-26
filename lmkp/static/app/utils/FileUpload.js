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
                        html: '',
                        flex: 1
                    }, {
                        xtype: 'container',
                        items: [
                            {
                                xtype: 'button',
                                iconCls: 'button-add-file',
                                // TODO
                                tooltip: 'new',
                                handler: function() {
                                    var win = me.createUploadWindow();
                                    win.show();
                                }
                            }
                        ]
                    }
                ]
            }
        ]

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
            fileObjects.push({
                name: filepanels[fp].fileName,
                identifier: filepanels[fp].fileIdentifier
            });
        }

        // Sort the objects by identifier
        fileObjects.sort(this.sort_by(
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
     * Function to add a single file panel
     */
    addSingleFilePanel: function(fileName, fileIdentifier) {
        var me = this;
        me.insert(0, {
            xtype: 'panel',
            name: 'filepanelwithcontent',
            // Store the values to the top panel as well to make them accessible
            // more easily
            fileName: fileName,
            fileIdentifier: fileIdentifier,
            border: 0,
            layout: {
                type: 'hbox'
            },
            items: [
                {
                    xtype: 'container',
                    name: 'filepanel_filename',
                    html: fileName,
                    flex: 1
                }, {
                    xtype: 'container',
                    defaults: {
                        margin: '0 0 2 2'
                    },
                    items: [
                        {
                            xtype: 'button',
                            iconCls: 'button-view-file',
                            // TODO
                            tooltip: 'view',
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
                            // TODO
                            tooltip: 'download',
                            handler: function() {
                                var fp = this.up('panel[name=filepanelwithcontent]');
                                if (fp && fp.fileIdentifier) {
                                    var url = '/files/download/' + fp.fileIdentifier;
                                    window.open(url, 'lo_fileview');
                                }
                            }
                        }, {
                            xtype: 'button',
                            iconCls: 'button-edit-file',
                            // TODO
                            tooltip: 'edit',
                            handler: function() {
                                var fp = this.up('panel[name=filepanelwithcontent]');
                                if (fp && fp.fileIdentifier && fp.fileName) {
                                    var win = me.editUploadWindow(fp.fileName, fp.fileIdentifier);
                                    win.show();
                                }
                            }
                        }, {
                            xtype: 'button',
                            iconCls: 'button-delete-file',
                            // TODO
                            tooltip: 'delete',
                            handler: function() {
                                var fp = this.up('panel[name=filepanelwithcontent]');
                                if (fp && fp.fileIdentifier && fp.fileName) {
                                    console.log("coming soon: function to delete file " + fp.fileName);
                                }
                            }
                        }
                    ]
                }
            ]
        });
    },

    /**
     * Function to replace the values of a file panel, for example after the
     * filename was edited.
     */
    replaceSingleFilePanel: function(fileName, fileIdentifier) {
        // Try to find the filepanel
        var filepanels = this.query('panel[name=filepanelwithcontent]');
        for (var fp in filepanels) {
            if (filepanels[fp].fileIdentifier == fileIdentifier) {
                filepanels[fp].fileName = fileName;
                var x =filepanels[fp].down('container[name=filepanel_filename]');
                if (x) {
                    x.update(fileName);
                }
            }
        }
    },

    /**
     * Show a window to edit a file, (so far) only filename can be edited.
     */
    editUploadWindow: function(fileName, fileIdentifier) {
        var me = this;
        var win = Ext.create('Ext.window.Window', {
            // TODO
            title: 'Edit existing file',
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
                            xtype: 'textfield',
                            name: 'filename',
                            fieldLabel: 'Name',
                            value: fileName,
                            maxLength: 500
                        }
                    ],
                    buttons: [
                        {
                            // TODO
                            text: 'Close',
                            handler: function() {
                                win.close();
                            }
                        }, '->', {
                            // TODO
                            text: 'Save',
                            handler: function() {
                                var form = this.up('form').getForm();
                                if (form.isValid()) {
                                    // Get the new filename and replace it in
                                    // the filepanel
                                    var values = form.getValues();
                                    me.replaceSingleFilePanel(
                                        values.filename,
                                        fileIdentifier
                                    );
                                    win.close();
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
     * Show a window to upload a new file.
     */
    createUploadWindow: function() {
        var me = this;
        var win = Ext.create('Ext.window.Window', {
            // TODO
            title: 'Upload new file',
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
                            // TODO
                            emptyText: 'Select a file',
                            fieldLabel: 'File',
                            name: 'file',
                            buttonText: 'Browse',
                            regex: /(.)+((\.gif)|(\.jpeg)|(\.jpg)|(\.png))$/i
                        }, {
                            xtype: 'panel',
                            data: {
                                fileExtensions: 'gif, jpeg, jpg, png',
                                maxFileSize: '5MB'
                            },
                            border: 0,
                            // TODO
                            tpl: 'Maximum file size: {maxFileSize}<br/>'
                                + 'Valid file extensions: {fileExtensions}'
                        }
                    ],
                    buttons: [
                        {
                            // TODO
                            text: 'Close',
                            handler: function() {
                                win.close();
                            }
                        }, '->', {
                            // TODO
                            text: 'Upload',
                            handler: function() {
                                var form = this.up('form').getForm();
                                if (form.isValid()) {
                                    form.submit({
                                        url: '/files/upload',
                                        // TODO
                                        waitMsg: 'Uploading ...',
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
     * Helper function to sort an array of json objects
     * http://stackoverflow.com/a/979325
     */
    sort_by: function(field, reverse, primer){
        var key = function (x) {return primer ? primer(x[field]) : x[field]};
        return function (a,b) {
            var A = key(a), B = key(b);
            return (A < B ? -1 : (A > B ? 1 : 0)) * [1,-1][+!!reverse];
        }
    }
});