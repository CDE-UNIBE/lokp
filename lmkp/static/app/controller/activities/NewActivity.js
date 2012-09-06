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
    }],

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
                click: this.onCreateNewStakeholderButtonClick
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
        var formpanel = this.getNewActivityForm();
        var taggroups = [];
        var stakeholders = [];

        // Get the geometry
        var geometry = null;
        var geojson = new OpenLayers.Format.GeoJSON();
        if (this.getMapPanel().getActivityGeometry()) {
            var editorMapController = this.getController('editor.Map');
            geometry = Ext.decode(geojson.write(
                editorMapController.getActivityGeometryFromMap(true)
            ));
        }

        // Collect Stakeholder information
        var shFieldset = this.getSelectStakeholderFieldSet();
        var shComps = shFieldset.query('lo_stakeholderfieldcontainer');
        for(var j = 0; j < shComps.length; j++ ) {
            var fieldContainer = shComps[j];
            var stakeholder = {}
            stakeholder['id'] = fieldContainer.getStakeholderId();
            //stakeholder['role'] = fieldContainer.getStakeholderRole();
            stakeholder['role'] = 6;
            stakeholder['version'] = fieldContainer.getStakeholderVersion();
            stakeholder['op'] = 'add';
            stakeholders.push(stakeholder);
        }

        // Loop through each form panel (they form taggroups)
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
                        main_tag.value = c.getValueValue()
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
            'activities': [{
                'taggroups': taggroups,
                'geometry': geometry,
                'stakeholders': stakeholders
            }]
        };

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

                    // Reset geometry of map panel
                    me.getMapPanel().setActivityGeometry(null);

                    // If mappopup still there, remove it
                    var popup = (
                        Ext.ComponentQuery.query('window[itemId=mappopup]').length > 0)
                        ? Ext.ComponentQuery.query('window[itemId=mappopup]')[0]
                        : null;
                    if (popup) popup.destroy();

                    // Close form window
                    var win = formpanel.up('window');
                    win.destroy();

                    var fieldContainers = formpanel.query('lo_stakeholderfieldcontainer');
                    for(var i = 0; i < fieldContainers.length; i++){
                        this.getSelectStakeholderFieldSet().remove(fieldContainers[i]);
                    }

                    // Remove also the feature on the map
                    this.getMapPanel().getVectorLayer().removeAllFeatures();
                } else {
                    Ext.Msg.alert('Failure', 'The activity could not be created.');
                }
            },
            scope: this
       });
    },

    /**
     * Show a window containing the form to add a new Activity.
     * {item}: Optional possibility to provide an existing item (instance of
     * model.Activity)
     */
    showNewActivityWindow: function(item) {
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
                shPanel.showForm();
                // Put everything in a window and show it.
                var activityEdit = (item != null);
                var win = Ext.create('Lmkp.view.public.NewActivityWindow', {
                    aPanel: aPanel,
                    shPanel: shPanel,
                    activityEdit: activityEdit
                });
                win.show();
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

        // Disable buttons if no other cards next to it
        Ext.getCmp('card-prev').setDisabled(!layout.getPrev());
        Ext.getCmp('card-next').setDisabled(!layout.getNext());

        // Enable the submit button if the last card is shown or if an Activity
        // is edited
        var tbar = button.up('toolbar');
        var submitbutton = tbar.down('button[itemId=submitButton]');
        if (!layout.getNext() || panel.activityEdit) {
            submitbutton.enable();
        } else {
            submitbutton.disable();
        }
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
            // Insert stakeholder into fieldset above
            var fieldset = this.getSelectStakeholderFieldSet();
            fieldset.insert(0, {
                stakeholder: shpanel.contentItem,
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
    onCreateNewStakeholderButtonClick: function() {

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
                shPanel.showForm(mandatoryStore, completeStore);
                // Put everything in a window and show it
                var win = Ext.create('Ext.window.Window', {
                    title: 'Create new Stakeholder',
                    autoScroll: true,
                    border: 0,
                    layout: 'fit',
                    items: shPanel
                });
                win.show();
            });
        });
    },

    /**
     * Append newly created Stakeholder (this happens in separate window) to 
     * fieldset with involved Stakeholders
     * {stakeholder}: Instance of model.Stakeholder
     */
    _onNewStakeholderCreated: function(stakeholder) {

        var sel = this.getStakeholderSelection();
        var form = sel.down('form');

        if (stakeholder) {
            // Insert stakeholder into fieldset above
            var fieldset = this.getSelectStakeholderFieldSet();
            fieldset.insert(0, {
                stakeholder: stakeholder,
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
});