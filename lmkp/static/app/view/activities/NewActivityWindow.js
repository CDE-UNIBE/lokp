Ext.define('Lmkp.view.activities.NewActivityWindow', {
	extend: 'Ext.window.Window',
	
	title: 'Add new Activity',
	
	layout: 'fit',
	defaults: {
		border: 0
	},

	initComponent: function() {
		Ext.Ajax.request({
			url: '/config/form',
			success: function(response) {
				var formConfig = Ext.decode(response.responseText);
				
				var form = Ext.create('Ext.form.Panel', {
					url: '',
					border: 0,
					bodyPadding: 5,
					layout: 'anchor',
					defaults: {
						anchor: '100%'
					},
					items: formConfig
				});
				this.add(form);
			}, scope: this
		});
		
		this.callParent(arguments);
	}
});
