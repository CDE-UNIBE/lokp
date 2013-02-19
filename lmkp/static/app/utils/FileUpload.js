Ext.define('Lmkp.utils.FileUpload', {
    extend: 'Ext.container.Container',

    layout: {
        type: 'vbox',
        align: 'stretch'
    },

//    items: [
//        {
//            xtype: 'panel',
//            border: 0,
//            layout: {
//                type: 'hbox'
//            },
//            items: [
//                {
//                    xtype: 'container',
//                    html: 'No file yet.',
//                    flex: 1
//                }, {
//                    xtype: 'container',
//                    items: [
//                        {
//                            xtype: 'button',
//                            text: 'n',
//                            tooltip: 'new',
//                            handler: function(button) {
//                                var p = button.up('[name=newtaggrouppanel_value]');
//                                var win = p.createUploadWindow();
//                                win.show();
//                            }
//                        }
//                    ]
//                }
//            ]
//        }
//    ],

    initComponent: function() {

        console.log("initComponent");
        console.log(this);

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
                        html: 'No file yet.',
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
     * Custom function to set a predefined value
     */
    setValue: function(value) {

        var me = this;

        var v = value.split(',');
        for (var i in v) {
//            console.log(v[i]);
            me.insert(0, {
            xtype: 'panel',
                border: 0,
                layout: {
                    type: 'hbox'
                },
                items: [
                    {
                        xtype: 'container',
                        html: v[i],
                        flex: 1
                    }, {
                        xtype: 'container',
                        items: [
                            {
                                xtype: 'button',
                                text: 'e',
                                tooltip: 'edit',
                                oldValue: v[i], // Store the value to button
                                handler: function() {
                                    var win = me.editUploadWindow(this.oldValue);
                                    win.show();
                                }
                            }, {
                                xtype: 'button',
                                text: 'd',
                                tooltip: 'delete',
                                oldValue: v[i],
                                handler: function() {
                                    console.log("coming soon: function to delete file " + this.oldValue);
                                }
                            }
                        ]
                    }
                ]
            });
        }
    },

    /**
     * Custom function to return the submit value when putting together the
     * form.
     */
    getSubmitValue: function() {
        return 'blabla';
    },

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

    createUploadWindow: function() {

        var win = Ext.create('Ext.window.Window', {
            title: 'Upload new file',
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
                            fieldLabel: 'Name'
                        }, {
                            xtype: 'filefield',
                            emptyText: 'Select a file',
                            fieldLabel: 'File',
                            name: 'file-path',
                            buttonText: 'Browse'
                        }
                    ],
                    buttons: [
                        {
                            text: 'Save',
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
    }
});