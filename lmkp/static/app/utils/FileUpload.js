Ext.define('Lmkp.utils.FileUpload', {
    extend: 'Ext.container.Container',

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

    initComponent: function() {

        // It is necessary to know the identifier of the current item. To do
        // this, try to query the form to edit the item.
        // So far, this only works for Activities.
        var form;
        var fQuery = Ext.ComponentQuery.query('form[itemId=newActivityForm]');
        if (fQuery.length > 0) {
            form = fQuery[0];
        }
        this.item_identifier = form.activity_identifier;

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
                                text: 'n',
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
        var values = Ext.JSON.decode(value);
        for (var v in values) {
            var cv = values[v];
            if (cv.name && cv.identifier) {
                this.addSingleFilePanel(cv.name, cv.identifier);
            }
        }
    },

    /**
     * Function to add a single file panel
     */
    addSingleFilePanel: function(fileName, fileIdentifier) {
        var me = this;
        me.insert(0, {
            xtype: 'panel',
            border: 0,
            layout: {
                type: 'hbox'
            },
            items: [
                {
                    xtype: 'container',
                    html: fileName,
                    flex: 1
                }, {
                    xtype: 'container',
                    items: [
                        {
                            xtype: 'button',
                            text: 's',
                            tooltip: 'show',
                            fileIdentifier: fileIdentifier,
                            handler: function() {
                                var url = '/files/show/';
                                if (me.item_identifier) {
                                    url += me.item_identifier;
                                } else {
                                    url += 'temp';
                                }
                                url += '/' + this.fileIdentifier;
                                window.open(url, 'lo_fileview');
                            }
                        }, {
                            xtype: 'button',
                            text: 'd',
                            tooltip: 'download',
                            fileIdentifier: fileIdentifier,
                            handler: function() {
                                var url = '/files/download/';
                                if (me.item_identifier) {
                                    url += me.item_identifier;
                                } else {
                                    url += 'temp';
                                }
                                url += '/' + this.fileIdentifier;
                                window.open(url, 'lo_fileview');
                            }
                        }, {
                            xtype: 'button',
                            text: 'e',
                            tooltip: 'edit',
                            fileIdentifier: fileIdentifier,
                            fileName: fileName,
                            handler: function() {
                                var win = me.editUploadWindow(this.fileName);
                                win.show();
                            }
                        }, {
                            xtype: 'button',
                            text: 'd',
                            tooltip: 'delete',
                            fileIdentifier: fileIdentifier,
                            fileName: fileName,
                            handler: function() {
                                console.log("coming soon: function to delete file " + this.fileName);
                            }
                        }
                    ]
                }
            ]
        });
    },

    /**
     * Custom function to return the submit value when putting together the
     * form.
     */
    getSubmitValue: function() {
        return 'blabla';
    },

    /**
     * Show a window to edit a file, (so far) only filename can be edited.
     */
    editUploadWindow: function(oldFile) {

        var win = Ext.create('Ext.window.Window', {
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
                            fieldLabel: 'Name',
                            value: oldFile
                        }
                    ],
                    buttons: [
                        {
                            text: 'Upload',
                            handler: function() {
                                var form = this.up('form').getForm();
                                if (form.isValid()) {
                                    console.log('submit');
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
                            tpl: 'Maximum file size: {maxFileSize}<br/>'
                                + 'Valid file extensions: {fileExtensions}'
                        }
                    ],
                    buttons: [
                        {
                            text: 'Close'
                        }, '->', {
                            text: 'Upload',
                            handler: function() {
                                var form = this.up('form').getForm();
                                if (form.isValid()) {
                                    form.submit({
                                        url: '/files/upload',
                                        waitMsg: 'Uploading ...',
                                        params: {
                                            identifier: me.item_identifier
                                        },
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
    }
});