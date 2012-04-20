Ext.define('Lmkp.view.activities.NewActivityWindow', {
	extend: 'Ext.window.Window',
	
	title: 'Add new Activity',
	
	layout: 'fit',
	defaults: {
		border: 0
	},

	initComponent: function() {
		var me = this;
		
		if (me.config) {
			var formConfig = me.config;
			
			// create validator functions where available
			for (var i=0; i<formConfig.length; i++) {
				if (formConfig[i]['validator']) {
					formConfig[i]['validator'] = new Function('value', formConfig[i]['validator']);
				}
			}
			// prepare the form
			var form = Ext.create('Ext.form.Panel', {
				url: '',
				border: 0,
				bodyPadding: 5,
				layout: 'anchor',
				defaults: {
					anchor: '100%'
				},
				buttons: [{
					formBind: true,
					disabled: true,
					text: 'Submit',
					handler: function() {
						// var form = this.up('form').getForm();
						// if (form.isValid()) {
							// form.submit({
								// success: function(form, action) {
									// console.log("success");
								// },
								// failure: function(form, action) {
									// console.log("failure");
								// }
							// });
						// }
						Ext.Msg.alert("Coming soon ...", "This functionality will be implemented soon ...");
					}
				}]
			});
			// prepare to highlight required fields when adding them to the form
			form.on('beforeadd', function(me, field) {
				if (!field.allowBlank) {
					field.labelSeparator += '<span style="color: rgb(255, 0, 0); padding-left: 2px;">*</span>';
				}
			});
			// add the fields to the form
			form.add(formConfig);
			// add the form to the window
			this.items = form;
		}

		this.callParent(arguments);
	}
});
