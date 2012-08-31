Ext.define('Lmkp.view.stakeholders.NewStakeholder', {
    extend: 'Lmkp.view.NewItem',

    alias: ['widget.lo_newstakeholderpanel'],

    config: {
        addedStakeholder: null
    },

    layout: 'fit',
    defaults: {
        border: 0
    },

    width: 400,

    initComponent: function(){



        //var form = this.down('form');
        // prepare the form
        var form = Ext.create('Ext.form.Panel', {
            autoScroll: true,
            border: 0,
            bodyPadding: 5,
            layout: 'anchor',
            defaults: {
                anchor: '100%'
            },
            buttons: [{
                iconCls: 'cancel-button',
                scale: 'medium',
                text: 'Cancel'
            },{
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
        var mandatoryStore = Ext.create('Lmkp.store.StakeholderConfig');
        mandatoryStore.filter("allowBlank", false);
        mandatoryStore.load();

        // load a store containing only the optional fields.
        // This is needed to keep track of all the optional fields available.
        var optionalStore_complete = Ext.create('Lmkp.store.StakeholderConfig');
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
        });

        this.items = form;
        
        this.callParent(arguments);
    }

});