Ext.define('Lmkp.view.users.UserWindow', {
    extend: 'Ext.window.Window',
    alias: ['widget.userwindow'],
	
    title: 'User Profile',
	
    layout: 'fit',
    defaults: {
        border: 0
    },
    width: 400,
	
    initComponent: function() {
        var me = this;
		
        if (me.username) {
			
            var activityChangesetStore = Ext.create('Lmkp.store.ActivityChangesets');
            // load only changeset from current user, initial status: active
            activityChangesetStore.getProxy().extraParams = {
                'user': me.username,
                'status': 'active' // when making changes here, also change initially selected value of ComboBox below
            };
            activityChangesetStore.load();
			
            // prepare status values
            var statusStore = Ext.create('Lmkp.store.Status').load();
			
            this.title = 'User profile of user ' + me.username;
            this.items = [{
                xtype: 'tabpanel',
                activeItem: 0,
                defaults: {
                    border: 0
                },
                items: [{
                    title: 'Overview',
                    loader: {
                        url: '/users/json/' + me.username,
                        autoLoad: true,
                        loadMask: true,
                        renderer: function(loader, response, active) {
                            var json = Ext.JSON.decode(response.responseText);
                            if (json.success) {
                                // prepare form
                                var form = Ext.create('Ext.form.Panel', {
                                    url: '/users/update',
                                    border: 0,
                                    bodyPadding: 5,
                                    layout: 'anchor',
                                    defaults: {
                                        anchor: '100%'
                                    }
                                });
                                // show only displayfield except when editing is allowed
                                var xt = 'displayfield';
                                if (json.editable) {
                                    xt = 'textfield'
                                }
                                // add field for username
                                form.add({
                                    xtype: 'displayfield', // username can never be changed
                                    fieldLabel: 'Username',
                                    value: json.data.username
                                });
                                // if email is visible (= available), show it
                                if (json.data.email) {
                                    form.add({
                                        xtype: xt,
                                        name: 'email',
                                        fieldLabel: 'E-Mail',
                                        value: json.data.email,
                                        vtype: 'email',
                                        allowBlank: false
                                    });
                                }
                                // TODO: allow to change passwords
                                // also add submit button if form is editable
                                if (json.editable) {
                                    // add hidden field to submit username
                                    form.add({
                                        xtype: 'hiddenfield',
                                        name: 'username',
                                        value: json.data.username
                                    });
                                    // add submit button
                                    form.addDocked({
                                        xtype: 'toolbar',
                                        dock: 'bottom',
                                        ui: 'footer',
                                        items: [
                                        {
                                            xtype: 'button',
                                            text: 'Change Password',
                                            handler: function() {
                                                var win = Ext.create('Lmkp.view.users.ChangePasswordWindow', {
                                                    username: json.data.username
                                                });
                                                win.show();
                                            }
                                        },
                                        {
                                            xtype: 'component',
                                            flex: 1
                                        },
                                        {
                                            xtype: 'button',
                                            text: 'Update',
                                            formBind: true,
                                            disabled: true,
                                            handler: function() {
                                                if (form.getForm().isValid()) {
                                                    form.getForm().submit({
                                                        success: function(form, action) {
                                                            Ext.Msg.alert('Success', action.result.msg);
                                                        },
                                                        failure: function(form, action) {
                                                            Ext.Msg.alert('Failure', action.result.msg);
                                                        }
                                                    });
                                                }
                                            }
                                        }
                                        ]
                                    });
                                }
                                // add all fields to form
                                loader.getTarget().add(form);
                            } else { // something went wrong (success == false), show error message
                                loader.getTarget().update(json.msg);
                            }
                        }
                    }
                }, {
                    title: 'Reported Activities',
                    items: [{
                        xtype: 'combobox',
                        store: statusStore,
                        valueField: 'db_name',
                        displayField: 'display_name',
                        fieldLabel: 'Filter by status',
                        queryMode: 'local',
                        value: statusStore.findRecord('db_name', 'active'), // initial status: active
                        listeners: {
                            select: function(combo, records, eOpts) {
                                // update status parameter of changeset store and reload it
                                activityChangesetStore.getProxy().extraParams = {
                                    'user': me.username,
                                    'status': records[0].get('db_name')
                                };
                                activityChangesetStore.load();
                            }
                        }
                    }, {
                        xtype: 'gridpanel',
                        store: activityChangesetStore,
                        columns: [{
                            // TODO: add name of activity to changeset
                            /**
                             * It would be much nicer to show the name of an activity rather
                             * than its UUID. But for the moment being, the changeset protocol
                             * does not provide the name of an activity.
                             */
                            header: 'Activity',
                            dataIndex: 'activity',
                            flex: 1
                        }, {
                            header: 'Status',
                            dataIndex: 'status'
                        }],
                        dockedItems: [{
                            xtype: 'pagingtoolbar',
                            store: activityChangesetStore,
                            dock: 'bottom',
                            enableOverflow: false,
                            displayInfo: true
                        }]
                    }]
                }]
            }]
        } else {
            this.items = [{
                xtype: 'panel',
                html: 'Something went wrong (no username found).'
            }]
        }
		
        this.callParent(arguments);
    }
});
