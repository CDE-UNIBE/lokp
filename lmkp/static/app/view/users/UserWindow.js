Ext.define('Lmkp.view.users.UserWindow', {
	extend: 'Ext.window.Window',
	alias: ['widget.userwindow'],
	
	title: 'User Profile',
	
	layout: 'fit',
	defaults: {
		border: 0
	},
	width: 400,
	height: 200,
	
	initComponent: function() {
		var me = this;
		
		if (me.username) {
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
									url: '',
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
									xtype: xt,
									name: 'username',
									fieldLabel: 'Username',
									value: json.data.username,
									allowBlank: false
								});
								// if email is visible (= available), show it
								if (json.data.email) {
									form.add({
										xtype: xt,
										name: 'email',
										fieldLabel: 'E-Mail',
										value: json.data.email,
										allowBlank: false
									});
								}
								// TODO: allow to change passwords
								// also add submit button if form is editable
								if (json.editable) {
									form.addDocked({
									    xtype: 'toolbar',
									    dock: 'bottom',
									    ui: 'footer',
									    items: [
									        { xtype: 'component', flex: 1 },
									        {
									        	xtype: 'button',
									        	text: 'Update',
									        	formBind: true,
									        	disabled: true,
									        	handler: function() {
									        		if (form.getForm().isValid()) {
									        			Ext.Msg.alert('Soon ...', 'Functionality coming soon ...');
									        			// TODO: implement this
									        			// form.getForm.submit({
									        				// success: function(form, action) {
									        					// // ...
									        				// },
									        				// failure: function(form, action) {
									        					// // ...
									        				// }
									        			// });
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
					html: 'Coming soon ...'
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
