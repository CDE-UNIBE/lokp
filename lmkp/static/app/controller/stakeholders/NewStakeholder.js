Ext.define('Lmkp.controller.stakeholders.NewStakeholder', {
    extend: 'Ext.app.Controller',

    views: [
    'stakeholders.NewStakeholder'
    ],

    refs: [
        {
            ref: 'newStakeholderForm',
            selector: 'lo_newstakeholderpanel form[itemId=newStakeholderForm]'
        }
    ],

    init: function(){
        // Use some functionalities already defined in
        // controller.activities.NewActivity
        var newActivityController = this.getController('activities.NewActivity');
        this.control({
            'lo_newstakeholderpanel button[itemId="cancelButton"]': {
                click: this.onCancelButtonClick
            },
            'lo_newstakeholderpanel button[itemId="submitButton"]': {
                click: this.onSubmitButtonClick
            },
            'lo_newstakeholderpanel button[name=addAdditionalTagButton]': {
                click: newActivityController.onAddAdditionalTagButtonClick
            },
            'lo_newstakeholderpanel button[itemId=addAdditionalTaggroupButton]': {
                click: this.onAddAdditionalTaggroupButtonClick
            },
            // Intercept normal functionality of button (defined in
            // Lmkp.view.activities.NewTaggroupPanel)
            'lo_newstakeholderpanel button[name=deleteTag]': {
                click: newActivityController.onDeleteTagButtonClick
            }
        });
    },

    onCancelButtonClick: function(button, event, eOpts){
        button.up('window').destroy();
    },

    onSubmitButtonClick: function(button, event, eOpts){
        var me = this;
        var formpanel = this.getNewStakeholderForm();
        var taggroups = [];

        // Loop through each form panel
        var forms = formpanel.query('form[name=taggroupfieldset]');
        for (var i in forms) {
            var tags = [];
            var main_tag = new Object();
            // Within a taggroup, loop through each tag
            var tgpanels = forms[i].query('lo_newtaggrouppanel');
            for (var j in tgpanels) {
                var c = tgpanels[j];
                // Only add Tags where Value or Key are not empty
                if (c.getKeyValue() != null && c.getValueValue() != null) {
                    tags.push({
                        'key': c.getKeyValue(),
                        'value': c.getValueValue(),
                        'op': 'add'
                    });
                    if (c.isMainTag()) {
                        main_tag.key = c.getKeyValue();
                        main_tag.value = c.getValueValue();
                    }
                }
            }
            if (tags.length > 0) {
                taggroups.push({
                    'tags': tags,
                    'main_tag': main_tag
                });
            }
        }

        // Put together the diff object.
        var diffObject = {
            'stakeholders': [{
                'taggroups': taggroups
            }]
        };

        // send the diff JSON through AJAX request
        Ext.Ajax.request({
            url: '/stakeholders',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            },
            jsonData: diffObject,
            callback: function(options, success, response) {
                if (success) {
                    Ext.Msg.alert('Success', 'The stakeholder was successfully created. It will be reviewed shortly.');

                    // Put newly created Stakeholder into a store.
                    var store = Ext.create('Ext.data.Store', {
                        autoLoad: true,
                        model: 'Lmkp.model.Stakeholder',
                        data : Ext.decode(response.responseText),
                        proxy: {
                            type: 'memory',
                            reader: {
                                root: 'data',
                                type: 'json',
                                totalProperty: 'total'
                            }
                        }
                    });

                    // Add newly created Stakeholder to fieldset in other
                    // window
                    var newActivityController =
                        me.getController('activities.NewActivity');
                    newActivityController._onNewStakeholderCreated(
                        store.getAt(0)
                    );

                    // Close form window
                    formpanel.up('window').close();
                    
                } else {
                    Ext.Msg.alert('Failure', 'The stakeholder could not be created.');
                }
            },
            scope: this
        });
    },

    /**
     * Adds an additional TagGroup panel to the form.
     */
    onAddAdditionalTaggroupButtonClick: function(button) {
        var form = button.up('form');
        var panel = form.up('panel');

        if (form && panel) {
            // create the stores
            var mainStore = Ext.create('Lmkp.store.StakeholderConfig');
            mainStore.load(function() {
                // Create and load a second store with all keys
                var completeStore = Ext.create('Lmkp.store.StakeholderConfig');
                completeStore.load(function() {
                    // When loaded, show panel
                    var fieldset = panel._getFieldset();
                    fieldset.add(panel._getSingleFormItem(
                        mainStore,
                        completeStore,
                        null
                    ));
                    // Insert it always at the bottom.
                    form.insert(form.items.length, fieldset);
                });
            });
        }
    }
});