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

    onSubmitButtonClick: function(){
        var me = this;
        var form = this.getNewStakeholderForm();
        var newTaggroups = [];
        var oldTaggroups = form.taggroups;

        // Collect Activity information
        var taggroupfieldsets = form.query('form[name=taggroupfieldset]');

        // Loop through each taggroup of form
        for (var i in taggroupfieldsets) {

            var taggroupfieldset = taggroupfieldsets[i];

            var newTags = [];
            var oldTags = [];
            var main_tag = new Object();
            var deletedTags = [];

            // Collect all old Tags of current Taggroup
            if (taggroupfieldset.oldTags) {
                for (var ot in taggroupfieldset.oldTags) {
                    if (taggroupfieldset.oldTags[ot]) {
                        oldTags.push({
                            id: taggroupfieldset.oldTags[ot].get('id'),
                            key: taggroupfieldset.oldTags[ot].get('key'),
                            value: taggroupfieldset.oldTags[ot].get('value')
                        });
                    }
                }
            }
            var initiallyEmpty = (oldTags.length == 0);

            // Loop through all current Tags of form
            var tagpanels = taggroupfieldset.query('lo_newtaggrouppanel');
            for (var ct in tagpanels) {
                var c = tagpanels[ct];
                // Only look at Tags where Key or Value is not empty
                if (c.getKeyValue() != null && c.getValueValue() != null) {

                    // Check if Tag has changed
                    if (c.getInitialValue() == c.getValueValue()
                        && c.getInitialKey() == c.getKeyValue()) {
                        // Tag has not changed. Find it in list with all old
                        // Tags and remove it from there
                        for (var findUnchangedTag in oldTags) {
                            if (oldTags[findUnchangedTag]
                                && oldTags[findUnchangedTag].id
                                    == c.getInitialTagId()) {
                                oldTags.splice(findUnchangedTag, 1);
                            }
                        }
                    } else {
                        // Tag has changed
                        // Add new Tag to list
                        newTags.push({
                            'key': c.getKeyValue(),
                            'value': c.getValueValue(),
                            'op': 'add'
                        });
                        // Check if it is a Main Tag
                        if (c.isMainTag()) {
                            main_tag.key = c.getKeyValue();
                            main_tag.value = c.getValueValue()
                        }
                        // If the Tag has an ID, it existed before.
                        if (c.getInitialTagId()) {
                            // Add it to list with deleted Tags
                            deletedTags.push({
                                'key': c.getInitialKey(),
                                'value': c.getInitialValue(),
                                'id': c.getInitialTagId(),
                                'op': 'delete'
                            });
                            // Delete it from list with the old tags
                            for (var findChangedTag in oldTags) {
                                if (oldTags[findChangedTag]
                                    && oldTags[findChangedTag].id
                                        == c.getInitialTagId()) {
                                    oldTags.splice(findChangedTag, 1);
                                }
                            }
                        }
                    }
                }
            }
            // After looping through each Tag of Taggroup, any remaining Tag in
            // the list of old Tags has been deleted since it is not in the form
            // anymore.
            for (var remainingTag in oldTags) {
                if (oldTags[remainingTag]) {
                    deletedTags.push({
                        'key': oldTags[remainingTag].key,
                        'value': oldTags[remainingTag].value,
                        'id': oldTags[remainingTag].id,
                        'op': 'delete'
                    });
                }
            }

            // Put together the diff for current Taggroup
            var diffTags = newTags.concat(deletedTags);

            if (diffTags.length > 0) {

                var diffTaggroup = {
                    tags: diffTags
                };
                if (main_tag.key && main_tag.value) {
                    diffTaggroup.main_tag = main_tag;
                }
                if (taggroupfieldset.taggroupId) {
                    diffTaggroup.id = taggroupfieldset.taggroupId;
                }
                if (taggroupfieldset.taggroupHistoryId) {
                    diffTaggroup.tg_id = taggroupfieldset.taggroupHistoryId;
                }
                if (initiallyEmpty) {
                    diffTaggroup.op = 'add';
                }

                newTaggroups.push(diffTaggroup);
            }

            // Taggroup was found and processed, remove it from list with old
            // Taggroups
            for (var findProcessedTaggroup in oldTaggroups) {
                if (oldTaggroups[findProcessedTaggroup]
                    && oldTaggroups[findProcessedTaggroup].id
                        == taggroupfieldset.taggroupId) {
                    oldTaggroups.splice(findProcessedTaggroup, 1);
                }
            }
        }

        // After looping through each Taggroup of the form, any remaining
        // Taggroup in the list of old Taggroups has been deleted since it is
        // not in the form anymore.
        var deletedTaggroups = [];
        for (var remainingTaggroup in oldTaggroups) {
            if (oldTaggroups[remainingTaggroup]) {
                var cTaggroup = oldTaggroups[remainingTaggroup];
                var dTags = [];
                // Loop through each Tag of Taggroup
                for (var t in cTaggroup.tags) {
                    dTags.push({
                        'key': cTaggroup.tags[t].get('key'),
                        'value': cTaggroup.tags[t].get('value'),
                        'id': cTaggroup.tags[t].get('id'),
                        'op': 'delete'
                    });
                }
                deletedTaggroups.push({
                    'id': cTaggroup.id,
                    'tg_id': cTaggroup.tg_id,
                    'op': 'delete',
                    'tags': dTags
                });
            }
        }

        var taggroups = newTaggroups.concat(deletedTaggroups);

        // Put together the diff object.
        var diffStakeholder = new Object();
        if (taggroups.length > 0) {
            diffStakeholder.taggroups = taggroups;
        }

        var diffObject;
        if (diffStakeholder.taggroups) {
            // Add identifier and version as well if available
            if (form.stakeholder_identifier) {
                diffStakeholder.id = form.stakeholder_identifier;
            }
            if (form.stakeholder_version) {
                diffStakeholder.version = form.stakeholder_version;
            }
            diffObject = {
                'stakeholders': [diffStakeholder]
            }
        }

        // send the diff JSON through AJAX request
        if (diffObject) {
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
                        form.up('window').close();

                        // Reload also the activity grid store
                        var shGridStore = Ext.data.StoreManager.lookup('StakeholderGrid');
                        if (shGridStore) {
                            shGridStore.load();
                        }

                        // If the edit came from the review, try to reload the
                        // taggroup store
                        var compareController = me.getController('moderation.CompareReview');
                        if (compareController && compareController.getCompareWindow()) {
                            compareController.reloadCompareTagGroupStore(
                                'compare',
                                'stakeholders',
                                diffStakeholder.id
                            );
                        }
                    } else {
                        Ext.Msg.alert('Failure', 'The stakeholder could not be created.');
                    }
                },
                scope: this
            });
        } else {
            // Nothing has changed, do nothing
            Ext.Msg.alert('No changes made', 'You did not make any changes.');
        }
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