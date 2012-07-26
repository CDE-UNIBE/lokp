Ext.define('Lmkp.view.activities.NewActivity', {
    extend: 'Lmkp.view.NewItem',

    alias: ['widget.lo_newactivitypanel'],

    requires: [
    'Lmkp.view.stakeholders.StakeholderFieldContainer'
    ],
	
    title: 'Add new Activity',

    config: {
        activityGeometry: null
    },
	
    layout: 'fit',
    defaults: {
        border: 0
    },
    width: 400,

    initComponent: function() {
		
        // prepare the form
        var form = Ext.create('Ext.form.Panel', {
            autoScroll: true,
            border: 0,
            bodyPadding: 5,
            layout: 'anchor',
            defaults: {
                anchor: '100%'
            },
            tbar: ['->',{
                disabled: true,
                formBind: true,
                iconCls: 'save-button',
                itemId: 'submitButton',
                scale: 'medium',
                scope: this,
                text: 'Submit'
            }]
        });
		
        // load a store containing only the mandatory fields.
        var mandatoryStore = Ext.create('Lmkp.store.ActivityConfig');
        mandatoryStore.filter("allowBlank", false);
        mandatoryStore.load();
    	
        // load a store containing only the optional fields.
        // This is needed to keep track of all the optional fields available.
        var optionalStore_complete = Ext.create('Lmkp.store.ActivityConfig');
        // for some reason, 'normal' filtering of stores does not work (asynchronous problem?)
        // instead, 'filtering' is done manually
        optionalStore_complete.on('load', function(store) {
            store.each(function(record) {
                if (record && record.get('allowBlank') != true) {
                    store.remove(record);
                }
            });
        });
        optionalStore_complete.load();

        // create a field for each mandatory attribute.
        mandatoryStore.on('load', function(store) {
            store.each(function(record) {
                form.up('panel')._getFormField(form, record, optionalStore_complete);
            });

            // After adding all mandatory fields, add the associated stakeholder
            // fieldset
            form.add({
                border: 1,
                itemId: 'selectStakeholderFieldSet',
                items: [
                {
                    itemId: 'selectStakeholderButton',
                    text: 'Add Stakeholder',
                    xtype: 'button'
                }],
                title: 'Associated Stakeholders',
                xtype: 'fieldset'
            });
        });

        this.items = form;

        this.callParent(arguments);
    } 
});
