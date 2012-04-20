Ext.define('Lmkp.view.users.ChangePasswordWindow', {
	extend: 'Ext.window.Window',
	
	title: 'Change Password',
	
	layout: 'fit',
	defaults: {
		border: 0
	},
	
	initComponent: function() {
		var me = this;
		
		if (me.username) {
			this.items = [{
				xtype: 'form',
				url: '/users/update',
				border: 0,
				bodyPadding: 5,
				layout: 'anchor',
				defaults: {
					anchor: '100%'
				},
				defaultType: 'textfield',
				items: [{
					inputType: 'password',
					fieldLabel: 'Old Password',
					name: 'old_password',
					allowBlank: false
				}, {
					inputType: 'password',
					fieldLabel: 'New Password',
					name: 'new_password1',
					allowBlank: false
				}, {
					inputType: 'password',
					fieldLabel: 'Repeat Password',
					name: 'new_password2',
					allowBlank: false,
					validator: function(value) {
						var pw1 = this.previousSibling('[name=new_password1]');
						return (value == pw1.getValue()) ? true : 'New passwords do not match.'
					}
				}, {
					xtype: 'hiddenfield',
					name: 'username',
					value: me.username
				}],
				buttons: [{
					formBind: true,
					disabled: true,
					text: 'Change',
					handler: function() {
						var win = this.up('window');
						var form = this.up('form').getForm();
						if (form.isValid()) {
							form.submit({
								success: function(theform, action) {
									Ext.Msg.alert('Success', action.result.msg);
									win.close();
								},
								failure: function(theform, action) {
									Ext.Msg.alert('Failure', action.result.msg);
								}
							});
						}
					}
				}]
			}];
		}
		this.callParent(arguments);
	}
});
