Ext.define('Lmkp.controller.activities.NewActivity', {
    extend: 'Ext.app.Controller',

    refs: [{
        ref: 'newActivityPanel',
        selector: 'lo_newactivitypanel'
    },{
        ref: 'selectStakeholderFieldSet',
        selector: 'lo_newstakeholderselection fieldset[itemId="selectStakeholderFieldSet"]'
    }, {
        ref: 'stakeholderSelection',
        selector: 'lo_stakeholderselection'
    }, {
        ref: 'newActivityForm',
        selector: 'lo_newactivitywindow lo_newactivitypanel form[itemId=newActivityForm]'
    }, {
        ref: 'mapPanel',
        selector: 'lo_publicmappanel'
    }, {
        ref: 'activityDetailWindow',
        selector: 'lo_activitydetailwindow'
    }, {
        ref: 'stakeholderDetailWindow',
        selector: 'lo_stakeholderdetailwindow'
    }],

    stores: [
        'ActivityGrid'
    ],

    views: [
    'public.NewActivityWindow',
    'activities.NewActivity',
    'stakeholders.StakeholderSelection',
    'stakeholders.NewStakeholder'
    ],

    init: function(){
        this.control({
            'lo_newactivitypanel button[name=addAdditionalTagButton]': {
                click: this.onAddAdditionalTagButtonClick
            },
            'lo_newactivitypanel button[itemId=addAdditionalTaggroupButton]': {
                click: this.onAddAdditionalTaggroupButtonClick
            },
            'lo_newactivitywindow button[itemId=submitButton]': {
                click: this.onSubmitButtonClick
            },
            // Intercept normal functionality of button (defined in
            // Lmkp.view.activities.NewTaggroupPanel)
            'lo_newactivitypanel lo_newtaggrouppanel button[name=deleteTag]': {
                click: this.onDeleteTagButtonClick
            },
            'lo_newactivitywindow button[id=card-next]': {
                click: this.onCardButtonClick
            },
            'lo_newactivitywindow button[id=card-prev]': {
                click: this.onCardButtonClick
            },
            'lo_stakeholderselection combo[itemId="searchTextfield"]': {
                select: this.onStakeholderSearchSelect
            },
            'lo_stakeholderselection button[itemId="clearButton"]':{
                click: this.onStakeholderClearButtonClick
            },
            'lo_stakeholderselection button[itemId="confirmButton"]': {
                click: this.onStakeholderSearchConfirmButtonClick
            },
            'lo_newstakeholderselection button[itemId=addNewStakeholderButton]': {
                click: this.showNewStakeholderWindow
            },
            'lo_stakeholderfieldcontainer button[name=stakeholderRemoveButton]': {
                click: this.onStakeholderRemoveButtonClick
            }
        });
    },

    /**
     * Remove a Tag from the form. If this Tag was the last one forming a
     * TagGroup, remove the entire TagGroup panel.
     * This actually adds additional functionality to the default behaviour when
     * clicking button to remove a TagGroup.
     * NOTE: This function is also used by
     * - controller.stakeholders.NewStakeholder
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

    /**
     * Adds an additional Tag to a TagGroup panel.
     * NOTE: This function is also used by
     * - controller.stakeholders.NewStakeholder
     */
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

    /**
     * Adds an additional TagGroup panel to the form.
     */
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
    },

    /**
     * Collect needed values (Activity, Stakeholder, geometry) and submit the
     * form to create a new Activity.
     */
    onSubmitButtonClick: function() {
        var me = this;
        var form = this.getNewActivityForm();
        var newTaggroups = [];
        var oldTaggroups = form.taggroups;

        // Get the geometry
        var geometry = null;
        if (this.getMapPanel()) {
            var geojson = new OpenLayers.Format.GeoJSON();
            if (this.getMapPanel().getNewFeatureGeometry()) {
                var editorMapController = this.getController('editor.Map');
                geometry = Ext.decode(geojson.write(
                    editorMapController.getActivityGeometryFromMap(true)
                ));
            }
        }

        // Collect Stakeholder (involvement) information
        var shFieldset = this.getSelectStakeholderFieldSet();
        // Make a real copy of the fieldset's involvements
        var oldInvolvements = [];
        for (var oi in shFieldset.involvements) {
            oldInvolvements.push(shFieldset.involvements[oi]);
        }
        var newStakeholders = [];
        var deletedStakeholders = [];

        // Get the stakeholders of the form 
        var shComps = shFieldset.query('lo_stakeholderfieldcontainer');
        for (var j = 0; j < shComps.length; j++ ) {
            var fieldContainer = shComps[j];
            
            // Try to find Involvement in list with existing Involvements
            var oldInvFound = false;
            for (var oiv in oldInvolvements) {
                var coiv = oldInvolvements[oiv];
                if (coiv.stakeholder.get('id')
                    == fieldContainer.getStakeholderId()
                    && coiv.stakeholder.get('version')
                    == fieldContainer.getStakeholderVersion()
                    && coiv.role_id == fieldContainer.getStakeholderRoleId()) {
                    // Stakeholder did not change, remove it from list with
                    // existing Stakeholders
                    oldInvolvements.splice(oiv, 1);
                    oldInvFound = true;
                }
            }
            
            if (oldInvFound == false) {
                // Involvement was not found in list with existing Involvements,
                // it must be a new one
                newStakeholders.push({
                    'id': fieldContainer.getStakeholderId(),
                    'role': fieldContainer.getStakeholderRoleId(),
                    'version': fieldContainer.getStakeholderVersion(),
                    'op': 'add'
                });
            }
        }
        
        // Any remaining Involvements in the list with existing Involvements has 
        // been deleted since it is not in the fieldContainer anymore
        for (var roi in oldInvolvements) {
            var croi = oldInvolvements[roi];
            deletedStakeholders.push({
                'id': croi.stakeholder.get('id'),
                'version': croi.stakeholder.get('version'),
                'role': croi.role_id,
                'op': 'delete'
            });
        }
        
        // Put new and deleted together for diff
        var stakeholders = newStakeholders.concat(deletedStakeholders);

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
                    if (taggroupfieldset.oldTags[ot].fields) {
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
                    diffTaggroup.tg_id = taggroupfieldset.taggroupHistoryId
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
                    if (cTaggroup.tags[t].modelName) {
                        dTags.push({
                            'key': cTaggroup.tags[t].get('key'),
                            'value': cTaggroup.tags[t].get('value'),
                            'id': cTaggroup.tags[t].get('id'),
                            'op': 'delete'
                        });
                    }
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
        var diffActivity = new Object();
        if (taggroups.length > 0) {
            diffActivity.taggroups = taggroups;
        }
        if (geometry) {
            diffActivity.geometry = geometry;
        }
        if (stakeholders.length > 0) {
            diffActivity.stakeholders = stakeholders;
        }

        var diffObject;
        if (diffActivity.taggroups || diffActivity.geometry
            || diffActivity.stakeholders) {
            // Add identifier and version as well if available
            if (form.activity_identifier) {
                diffActivity.id = form.activity_identifier;
            }
            if (form.activity_version) {
                diffActivity.version = form.activity_version;
            }
            diffObject = {
                'activities': [diffActivity]
            }
        }
        
        if (diffObject) {
            // Send the diff JSON through AJAX request
            Ext.Ajax.request({
                url: '/activities',
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json;charset=utf-8'
                },
                jsonData: diffObject,
                callback: function(options, success, response) {
                    if (success) {
                        Ext.Msg.alert('Success', 'The activity was successfully created. It will be reviewed shortly.');

                        var mapPanel = me.getMapPanel();
                        // Reset geometry of map panel
                        if (mapPanel) {
                            mapPanel.setNewFeatureGeometry(null);
                        }
	
                        // If mappopup still there, remove it
                        var popup = (
                            Ext.ComponentQuery.query('window[itemId=mappopup]').length > 0)
                        ? Ext.ComponentQuery.query('window[itemId=mappopup]')[0]
                        : null;
                        if (popup) popup.destroy();
	
                        // Close form window
                        var win = form.up('window');
                        win.destroy();
	
                        var fieldContainers = form.query('lo_stakeholderfieldcontainer');
                        for(var i = 0; i < fieldContainers.length; i++){
                            this.getSelectStakeholderFieldSet().remove(fieldContainers[i]);
                        }
	                    
                        // Refresh the detail window
                        var detailWindow = this.getActivityDetailWindow();
                        if (detailWindow) {
                            var historyStore = detailWindow.getHistoryStore();
                            if (historyStore) {
                                historyStore.load();
                            }
                        }
	
                        // Refresh the map with the new activities
                        if (mapPanel) {
                            // Reload the vector store
                            mapPanel.getActivityFeatureStore().load();
                            // Unselect all features on the helper vector layer
                            mapPanel.getNewFeatureSelectCtrl().unselectAll();
                            // Remove all features from the helper vector layer
                            mapPanel.getVectorLayer().removeAllFeatures();
                        }

                        // Reload also the activity grid store
                        var aGridStore = me.getActivityGridStore();
                        if (aGridStore) {
                            aGridStore.load();
                        }

                        // If the edit came from the review, try to reload the
                        // taggroup store
                        var compareController = me.getController('moderation.CompareReview');
                        if (compareController && compareController.getCompareWindow()) {
                            compareController.reloadCompareTagGroupStore(
                                'compare',
                                'activities',
                                diffActivity.id
                            );
                        }
                    } else {
                        Ext.Msg.alert('Failure', 'The activity could not be created.');
                    }
                },
                scope: this
            });
        } else {
            // Nothing was changed, do nothing
            Ext.Msg.alert('No changes made', 'You did not make any changes.');
        }
    },

    /**
     * Show a window containing the form to add a new Activity.
     * {item}: Optional possibility to provide an existing item (instance of
     * model.Activity)
     * {showPage}: Optional possibility to open the window at a given page
     * (0: Activity, 1: Involvements)
     */
    showNewActivityWindow: function(item, showPage) {
        var me = this;

        // Window to show that loading is in progress
        var loadingwin = Ext.create('Ext.window.Window', {
            title: Lmkp.ts.msg('gui_loading'),
            items: {
                html: Lmkp.ts.msg('gui_loading'),
                border: 0,
                bodyPadding: 5
            }
        });
        loadingwin.show();

        // Create and load a store with all mandatory keys
        var mandatoryStore = Ext.create('Lmkp.store.ActivityConfig');
        mandatoryStore.filter('allowBlank', false);
        mandatoryStore.load(function() {
            // Create and load a second store with all keys
            var completeStore = Ext.create('Lmkp.store.ActivityConfig');
            completeStore.load(function() {
                // When loaded, create and load panel for Activities
                var aPanel = Ext.create('Lmkp.view.activities.NewActivity', {
                    height: 500,
                    width: 400
                });
                aPanel.showForm(mandatoryStore, completeStore, item);
                // Also create and load panel for Stakeholders
                var shPanel = Ext.create('Lmkp.view.stakeholders.NewStakeholderSelection', {
                    height: 500,
                    width: 400
                });

                var involvedStakeholders = [];
                if (item) {
                    // Use Involvement store to get Stakeholders
                    var invStore = item.involvements();
                    invStore.each(function(inv) {
                        if (inv.raw.data) {
                            var shStore = Ext.create('Ext.data.Store', {
                                model: 'Lmkp.model.Stakeholder',
                                data: inv.raw.data,
                                proxy: {
                                    type: 'memory',
                                    reader: {
                                        type: 'json'
                                    }
                                }
                            });
                            shStore.load(function(stakeholders) {
                                // Each involvement only contains 1 Stakeholder.
                                // Also add information about the role of the
                                // Stakeholder.
                                involvedStakeholders.push({
                                    'stakeholder': stakeholders[0],
                                    'role': inv.get('role'),
                                    'role_id': inv.get('role_id')
                                });
                            });
                        }
                    });
                }

                shPanel.showForm(involvedStakeholders);
                // Put everything in a window and show it.
                var title = item ? Lmkp.ts.msg('activities_edit-activity')
                    .replace('{0}', item.get('version')) :
                    Lmkp.ts.msg('activities_add-new-activity');
                var activityEdit = (item != null);
                var win = Ext.create('Lmkp.view.public.NewActivityWindow', {
                    aPanel: aPanel,
                    shPanel: shPanel,
                    activityEdit: activityEdit,
                    showPage: showPage,
                    title: title
                });
                // Before showing the window, destroy loading window
                loadingwin.destroy();
                win.show();
                // If a page was provided, try to jump there
                if (showPage) {
                    var layout = win.getLayout();
                    var layoutitems = layout.getLayoutItems();
                    if (layoutitems[showPage]) {
                        layout.setActiveItem(showPage);
                    }
                }
                // Check buttons
                me._checkCardButtons(win.getLayout(), activityEdit);
            });
        });
    },

    /**
     * Switch between the cards (wizard-mode) of the form to add a new Activity.
     */
    onCardButtonClick: function(button) {
        
        var panel = button.up('panel');
        var layout = panel.getLayout();

        // Move to card
        layout[button._dir]();
        
        this._checkCardButtons(layout, panel.activityEdit);
    },
    
    /**
     * If a Stakeholder is selected in the search-combobox, show its details in
     * a panel below.
     */
    onStakeholderSearchSelect: function(combo, records){

        // Enable button
        var sel  = this.getStakeholderSelection();
        sel.confirmButton.enable();

        // Prepare stakeholder panel
        var p = Ext.create('Lmkp.view.stakeholders.StakeholderPanel', {
            contentItem: records[0],
            editable: false,
            border: 0
        });

        // Remove any previous stakeholder panel
        var form = sel.down('form');
        form.remove(form.down('lo_stakeholderpanel'))

        // Add stakeholder panel
        form.add(p);
    },

    /**
     * If the search-combobox for Stakeholders is cleared, remove any existing
     * details panel and reset search field.
     */
    onStakeholderClearButtonClick: function() {

        // Remove existing stakeholder panel
        var sel = this.getStakeholderSelection();
        var form = sel.down('form');
        var oldpanel = form.down('lo_stakeholderpanel');
        if (oldpanel) {
            form.remove(oldpanel);
        }

        // Disable button
        sel.confirmButton.disable();

        // Reset search field
        form.down('combo[itemId="searchTextfield"]').setValue(null);
    },

    /**
     * If a Stakeholder is selected from the search-combobox, reset the search
     * and add selected Stakeholder to fieldset.
     */
    onStakeholderSearchConfirmButtonClick: function() {

        var sel = this.getStakeholderSelection();
        var form = sel.down('form');
        var shpanel = form.down('lo_stakeholderpanel');

        if (shpanel) {
            var fieldset = this.getSelectStakeholderFieldSet();
            
            // If initial panel in fieldset still exists, remove it first
            if (fieldset.down('[itemId=initialText]')) {
                fieldset.remove(fieldset.down('[itemId=initialText]'));
            }
        	
            // Insert stakeholder into fieldset above
            fieldset.insert(0, {
                involvement: {
                    stakeholder: shpanel.contentItem,
                    role_id: 6 // Investor by default
                },
                xtype: 'lo_stakeholderfieldcontainer'
            });

            // Remove stakeholder panel
            form.remove(shpanel);

            // Reset search field
            form.down('combo[itemId="searchTextfield"]').setValue(null);

            // Disable button
            sel.confirmButton.disable();
        }
    },

    /**
     * If a new Stakeholder is to be created, show separate window to do so.
     */
    showNewStakeholderWindow: function(item) {

        // Window to show that loading is in progress
        var loadingwin = Ext.create('Ext.window.Window', {
            title: Lmkp.ts.msg('gui_loading'),
            items: {
                html: Lmkp.ts.msg('gui_loading'),
                border: 0,
                bodyPadding: 5
            }
        });
        loadingwin.show();

        // Make sure the item is an instance of model.Stakeholder
        if (!item.modelName || item.modelName != 'Lmkp.model.Stakeholder') {
            item = null;
        }

        // Create and load a store with all mandatory keys
        var mandatoryStore = Ext.create('Lmkp.store.StakeholderConfig');
        mandatoryStore.filter('allowBlank', false);
        mandatoryStore.load(function() {
            // Create and load a store with all keys
            var completeStore = Ext.create('Lmkp.store.StakeholderConfig');
            completeStore.load(function() {
                // When loaded, create and load panel for Stakeholders
                var shPanel = Ext.create('Lmkp.view.stakeholders.NewStakeholder', {
                    height: 500,
                    width: 400
                });
                shPanel.showForm(mandatoryStore, completeStore, item);
                // Put everything in a window and show it
                var title = item ?
                    Lmkp.ts.msg('stakeholders_edit-stakeholder').replace(
                        '{0}', item.get('version')) :
                    Lmkp.ts.msg('stakeholders_create-new-stakeholder');
                var win = Ext.create('Ext.window.Window', {
                    title: title,
                    autoScroll: true,
                    border: 0,
                    layout: 'fit',
                    items: shPanel
                });
                // Before showing the window, destroy loading window
                loadingwin.destroy();
                win.show();
            });
        });
    },
    
    /**
     * Remove a Stakeholder from the fieldset containing all the associated 
     * Stakeholders
     */
    onStakeholderRemoveButtonClick: function(button) {
        // If the last Stakeholder was removed, show initial Text again
        var fieldset = button.up('fieldset[itemId=selectStakeholderFieldSet]');
        if (fieldset.query('lo_stakeholderfieldcontainer').length == 1) {
            var selectionPanel = button.up('lo_newstakeholderselection');
            if (selectionPanel) {
                selectionPanel._showInitialText();
            }
        }
        // Remove fieldcontainer
        var fieldcontainer = button.up('lo_stakeholderfieldcontainer');
        fieldcontainer.destroy();
    },

    /**
     * If Stakeholder was newly created (this happens in separate window), 
     * append it to fieldset with involved Stakeholders.
     * {stakeholder}: Instance of model.Stakeholder
     */
    _onNewStakeholderCreated: function(stakeholder) {

        // Check if Stakeholder was created from Activity (new involvement)
        // panel
        var sel = this.getStakeholderSelection();
        if (sel) {
        	
            // Add new stakeholder to fieldset
            var form = sel.down('form');

            if (stakeholder) {
                var fieldset = this.getSelectStakeholderFieldSet();
                // If initial panel in fieldset still exists, remove it first
                if (fieldset.down('[itemId=initialText]')) {
                    fieldset.remove(fieldset.down('[itemId=initialText]'));
                }
            	
                // Insert stakeholder into fieldset above
                fieldset.insert(0, {
                    involvement: {
                        stakeholder: stakeholder,
                        role_id: 6 // Investor by default
                    },
                    xtype: 'lo_stakeholderfieldcontainer'
                });

                // Remove stakeholder panel
                if (form.down('lo_stakeholderpanel')) {
                    form.remove(form.down('lo_stakeholderpanel'));
                }

                // Reset search field
                form.down('combo[itemId="searchTextfield"]').setValue(null);

                // Disable button
                sel.confirmButton.disable();
            }
        }
        
        // Check if Stakeholder was created / edited from detail window.
        var detailWindow = this.getStakeholderDetailWindow();
        if (detailWindow) {
            // Try to find historyStore to reload it
            var historyStore = detailWindow.getHistoryStore();
            if (historyStore) {
                historyStore.load();
            }
        }
    },
    
    _checkCardButtons: function(layout, activityEdit) {
        // Disable buttons if no other cards next to it
        Ext.getCmp('card-prev').setDisabled(!layout.getPrev());
        Ext.getCmp('card-next').setDisabled(!layout.getNext());
        
        // Enable the submit button if the last card is shown or if an Activity
        // is edited
        var submitbutton_q = Ext.ComponentQuery.query('button[itemId=submitButton]');
        if (submitbutton_q && submitbutton_q.length > 0) {
            var submitbutton = submitbutton_q[0];
            if (!layout.getNext() || activityEdit) {
                submitbutton.enable();
            } else {
                submitbutton.disable();
            }
        }
    }
});