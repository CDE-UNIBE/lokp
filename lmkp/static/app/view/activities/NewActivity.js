Ext.define('Lmkp.view.activities.NewActivity', {
    extend: 'Lmkp.view.NewItem',

    alias: ['widget.lo_newactivitypanel'],

    requires: [
    'Lmkp.view.stakeholders.StakeholderFieldContainer',
    'Lmkp.view.activities.NewTaggroupPanel'
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
            tbar: [
                {
                    iconCls: 'add-info-button',
                    itemId: 'addAdditionalTaggroupButton',
                    scale: 'medium',
                    text: 'Add further information'
                }
            ]
        });

        this.items = form;

        this.callParent(arguments);
    },

    showForm: function(mandatoryStore, completeStore) {

        var me = this;
        var form = this.down('form');

        // Delete all existing items
        form.removeAll();

        // Collect all records of completeStore
        var all_records = [];
        completeStore.each(function(r){
            all_records.push(r.copy());
        });

        // Add a fieldset for each mandatory Key
        mandatoryStore.each(function(record) {
            // All keys should be available for each fieldset -> 'copy' store
            var main_store = Ext.create('Lmkp.store.ActivityConfig');
            main_store.add(all_records);

            form.add(me._getFieldset(
                main_store,
                completeStore,
                record.get('name')
            ));
        });

        // Add a button to add a new taggroup
        form.add({
            xtype: 'fieldset',
            border: 0,
            layout: 'hbox',
            items: [
                {
                    // Empty panel for spacing
                    xtype: 'panel',
                    border: 0,
                    flex: 1
                }, {
                    xtype: 'button',
                    itemId: 'submitButton',
                    iconCls: 'save-button',
                    scale: 'medium',
                    text: 'Submit'
                }
            ]
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
    },

    _getFieldset: function(mainStore, completeStore, initial_key) {
        return {
            xtype: 'form',
            name: 'taggroupfieldset',
            bodyPadding: 5,
            margin: '0 0 10 0',
            defaults: {
                margin: 0
            },
            // Toolbar to add additional Tags to Tag Group
            tbar: ['->', 
                {
                    xtype: 'button',
                    name: 'addAdditionalTagButton',
                    text: 'Add more information'
                }
            ],
            items: [
                {
                    xtype: 'lo_newtaggrouppanel',
                    is_maintag: true,
                    removable: true,
                    main_store: mainStore,
                    complete_store: completeStore,
                    initial_key: initial_key
                }
            ]
        }
    }
});