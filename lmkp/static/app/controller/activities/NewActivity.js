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
            },
            // Intercept normal functionality of button (defined in
            // Lmkp.view.activities.NewTaggroupPanel)
            'lo_newactivitypanel lo_newtaggrouppanel button[name=deleteTag]': {
                click: this.onDeleteTagButtonClick
            }
        });
    },

    /**
     * If the last item of a form is to be removed, destroy entire form panel.
     */
    onDeleteTagButtonClick: function(button) {
        var form = button.up('form');
        if (form && form.items.length == 1) {
            // Disable form first in order to keep track of fields that are not
            // allowed blank
            form.disable();
            form.destroy();
        }
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
        var form = button.up('form');
        var newtaggrouppanel = form.down('lo_newtaggrouppanel')
        if (form && newtaggrouppanel) {
            form.add({
                xtype: 'lo_newtaggrouppanel',
                is_maintag: false,
                removable: true,
                main_store: newtaggrouppanel.main_store,
                complete_store: newtaggrouppanel.complete_store
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