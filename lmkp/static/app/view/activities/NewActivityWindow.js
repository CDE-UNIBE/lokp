Ext.define('Lmkp.view.activities.NewActivityWindow', {
	extend: 'Ext.window.Window',
	
	title: 'Add new Activity',
	
	layout: 'fit',
	defaults: {
		border: 0
	},
	width: 400,

	initComponent: function() {
		// var me = this;
		
		// prepare the form
		var form = Ext.create('Ext.form.Panel', {
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
					var theform = this.up('form').getForm();
					if (theform.isValid()) {
						/*
						// The form cannot be submitted 'normally' because ActivityProtocol expects a JSON object.
						// As a solution, the form values are used to create a JSON object which is sent using an
						// AJAX request.
						// http://www.sencha.com/forum/showthread.php?132082-jsonData-in-submit-action-of-form
						
						// for the moment being, create dummy geometry
						var geometry = {'type': 'POINT', 'coordinates': [46.951081, 7.438637]}
						
						// put JSON together (new Activities per definition only contain one TagGroup)
						var jsonData = {'data': [{'geometry': geometry, 'taggroups': [form.getValues()]}]};
	
						// send JSON through AJAX request
						Ext.Ajax.request({
							url: '/activities',
							method: 'POST',
							headers: {'Content-Type': 'application/json;charset=utf-8'},
							jsonData: jsonData,
							success: function() {
								Ext.Msg.alert('Success', 'The activity was successfully created. It will be reviewed shortly.');
								form.up('window').close();
							},
							failure: function() {
								Ext.Msg.alert('Failure', 'The activity could not be created.');
							}
						});
						*/
						console.log("coming soon");
					}
				}
			}]
		});
		
		
		var mandatoryStore = Ext.create('Lmkp.store.Config');
    	mandatoryStore.filter("allowBlank", false);
    	mandatoryStore.load();
    			
		mandatoryStore.on('load', function(store) {
			store.each(function(record) {
				form.add(form.up('window')._getFormField(record));
			});
		});
		
		
		this.items = form;
		
		/**
		var mandatoryStore = Ext.create('Lmkp.store.Config');
    	mandatoryStore.filter("allowBlank", false);
    	mandatoryStore.load(function(records, operation, success) {
    		console.log(records);
    	});
    	// apply filter (allowBlank == false)
    	console.log(mandatoryStore);
		
		mandatoryStore.each(function(record) {
			console.log("bla");
			console.log(record);
		});
		*/
		
		
		
		/**
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
						var theform = this.up('form').getForm();
						if (theform.isValid()) {
							// The form cannot be submitted 'normally' because ActivityProtocol expects a JSON object.
							// As a solution, the form values are used to create a JSON object which is sent using an
							// AJAX request.
							// http://www.sencha.com/forum/showthread.php?132082-jsonData-in-submit-action-of-form
							
							// for the moment being, create dummy geometry
							var geometry = {'type': 'POINT', 'coordinates': [46.951081, 7.438637]}
							
							// put JSON together (new Activities per definition only contain one TagGroup)
							var jsonData = {'data': [{'geometry': geometry, 'taggroups': [form.getValues()]}]};

							// send JSON through AJAX request
							Ext.Ajax.request({
								url: '/activities',
								method: 'POST',
								headers: {'Content-Type': 'application/json;charset=utf-8'},
								jsonData: jsonData,
								success: function() {
									Ext.Msg.alert('Success', 'The activity was successfully created. It will be reviewed shortly.');
									form.up('window').close();
								},
								failure: function() {
									Ext.Msg.alert('Failure', 'The activity could not be created.');
								}
							});
						}
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
			
			// temp
			// form.add({
				// xtype: 'checkboxfield',
				// boxLabel: 'Add additional information',
				// submitValue: false,
				// handler: function(checkbox, checked) {
					// if (checked) {
						// Ext.Msg.alert('Coming soon ...', 'Here, the functionality to directly specify additional TagGroups in a next step will have to be implemented. See also discussion on Trac.');
					// }
				// }
			// });
			
			// add the form to the window
			this.items = form;
		}
		*/

		this.callParent(arguments);
	},
	
	_getFormField: function(record) {
		var t = Ext.create('Ext.form.field.Combobox', {
			fieldLabel: record.get('name')
		});
		return t;
	}
});
