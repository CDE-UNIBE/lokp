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
						url: '/users/' + me.username,
						autoLoad: true,
						loadMask: true
					}
				}, {
					title: 'Reported Activities',
					loader: {
						url: '/users/user1',
						autoLoad: true
					}
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
