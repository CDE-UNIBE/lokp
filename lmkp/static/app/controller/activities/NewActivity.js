Ext.define('Lmkp.controller.activities.NewActivity', {
    extend: 'Ext.app.Controller',

    refs: [{
        ref: 'newActivityPanel',
        selector: 'lo_newactivitypanel'
    },{
        ref: 'selectStakeholderFieldSet',
        selector: 'lo_newactivitypanel fieldset[itemId="selectStakeholderFieldSet"]'
    }],

    views: [
    'activities.NewActivity'
    ],

    init: function(){
        this.control({
            'lo_newactivitypanel button[itemId="selectStakeholderButton"]': {
                click: this.onStakeholderButtonClick
            },
            'lo_newactivitypanel button[name=addAdditionalTagButton]': {
                click: this.onAddAdditionalTagButtonClick
            },
            'lo_newactivitypanel button[itemId=addAdditionalTaggroupButton]': {
                click: this.onAddAdditionalTaggroupButtonClick
            }
        });
    },

    onStakeholderButtonClick: function(button, event){
        var sel = Ext.create('Lmkp.view.stakeholders.StakeholderSelection');

        var w = this.getNewActivityPanel();

        sel.on('close', function(panel, eOpts){
            var sh = panel.getSelectedStakeholder();
            this.getSelectStakeholderFieldSet().insert(
                0, {
                    stakeholder: sh,
                    xtype: 'lo_stakeholderfieldcontainer'
                });
        }, this);
        sel.show();
    },

    onAddAdditionalTagButtonClick: function(button) {
        var fieldset = button.up('fieldset');
        var newtaggrouppanel = fieldset.down('lo_newtaggrouppanel');
        if (fieldset && newtaggrouppanel) {
            fieldset.add({
                xtype: 'lo_newtaggrouppanel',
                is_maintag: true,
                removable: true,
                main_store: newtaggrouppanel.main_store,
                complete_store: newtaggrouppanel.complete_store,
                right_field: {
                    xtype: 'button',
                    name: 'addAdditionalTagButton',
                    text: '[+] Add',
                    margin: '0 0 0 5',
                    tooltip: 'Add additional information'
                }
            });
        }
    },

    onAddAdditionalTaggroupButtonClick: function(button) {
        var form = button.up('form');
        var panel = form.up('panel');

        if (form && panel) {
            // create the stores
            var mainStore = Ext.create('Lmkp.store.ActivityConfig');
            mainStore.load(function() {
                // Create and load a second store with all keys
                var completeStore = Ext.create('Lmkp.store.ActivityConfig');
                completeStore.load(function() {
                    // When loaded, show panel
                    form.insert(form.items.length - 2, panel._getFieldset(
                        mainStore,
                        completeStore,
                        null
                    ));
                });
            });
        }
    }

});