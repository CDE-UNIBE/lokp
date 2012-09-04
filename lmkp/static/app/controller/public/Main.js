Ext.define('Lmkp.controller.public.Main', {
    extend: 'Ext.app.Controller',

    requires: [
        'Ext.form.field.Hidden',
        'Lmkp.utils.StringFunctions',
        'Lmkp.view.activities.Details',
        'Lmkp.view.stakeholders.Details',
        'Lmkp.view.comments.ReCaptcha',
        'Lmkp.view.activities.NewActivity'
    ],

    refs: [{
        ref: 'mapPanel',
        selector: 'lo_publicmappanel'
    },{
        ref: 'showPendingActivitiesCheckbox',
        selector: 'checkbox[itemId="showPendingActivitiesCheckbox"]'
    },{
        ref: 'showPendingStakeholdersCheckbox',
        selector: 'checkbox[itemId="showPendingStakeholdersCheckbox"]'
    }, {
        ref: 'activityTablePanel',
        selector: 'lo_publicactivitytablepanel'
    }, {
        ref: 'stakeholderTablePanel',
        selector: 'lo_publicstakeholdertablepanel'
    }, {
    	ref: 'activityGridTopToolbar',
    	selector: 'toolbar[id=activityGridTopToolbar]'
    }, {
        ref: 'stakeholderGridTopToolbar',
        selector: 'toolbar[id=stakeholderGridTopToolbar]'
    }],

    stores: [
    'ActivityGrid',
    'ActivityConfig',
    'StakeholderGrid',
    'StakeholderConfig',
    ],

    init: function() {
        // Get the config stores and load them
        this.getActivityConfigStore().load();
        this.getStakeholderConfigStore().load();

        this.control({
            'lo_publicactivitytablepanel': {
                render: this.onActivityTablePanelRender
            },
            'lo_activitydetailwindow': {
                beforeshow: this.onActivityDetailWindowBeforeShow
            },
            'lo_publicstakeholdertablepanel': {
                render: this.onStakeholderTablePanelRender
            },
            'lo_publicactivitytablepanel gridpanel[itemId=activityGrid]': {
                selectionchange: this.onTableSelectionChange
            },
            'lo_publicactivitytablepanel gridpanel templatecolumn[name=showDetailsColumn]': {
                click: this.onShowDetailsColumnClick
            },
            'lo_publicactivitytablepanel button[itemId=activityFilterButton]': {
                click: this.onActivityFilterButtonClick
            },
            'lo_publicactivitytablepanel button[itemId=activityResetSelectionButton]': {
                click: this.onClearSelectionButtonClick
            },
            'lo_publicactivitytablepanel button[itemId=activityDeleteAllFiltersButton]': {
                click: this.onActivityDeleteAllFiltersButtonClick
            },
            'lo_publicactivitytablepanel button[itemId=newActivityButton]': {
            	click: this.onNewActivityButtonClick
            },
            'lo_publicstakeholdertablepanel gridpanel[itemId=stakeholderGrid]': {
                selectionchange: this.onTableSelectionChange
            },
            'lo_publicstakeholdertablepanel gridpanel templatecolumn[name=showDetailsColumn]': {
                click: this.onShowDetailsColumnClick
            },
<<<<<<< HEAD
            'gridpanel[itemId=stakeholderGrid] gridcolumn[name=stakeholdernamecolumn]': {
                afterrender: this.onStakeholderNameColumnAfterrender
            },
            'gridpanel[itemId=stakeholderGrid] gridcolumn[name=stakeholdercountrycolumn]': {
                afterrender: this.onStakeholderCountryColumnAfterrender
            },
            'lo_publicactivitytablepanel button[itemId=activityFilterButton]': {
                click: this.onActivityFilterButtonClick
            },
            'lo_publicactivitytablepanel button[itemId=activityResetSelectionButton]': {
                click: this.onClearSelectionButtonClick
            },
            'lo_publicactivitytablepanel checkbox[itemId="showPendingActivitiesCheckbox"]': {
                change: this.onShowPendingActivitiesCheckboxChange
            },
=======
>>>>>>> b33bd569272e76068610f61b46170f8031a005f6
            'lo_publicstakeholdertablepanel button[itemId=stakeholderFilterButton]': {
                click: this.onStakeholderFilterButtonClick
            },
            'lo_publicstakeholdertablepanel button[itemId=stakeholderResetSelectionButton]': {
                click: this.onClearSelectionButtonClick
            },
<<<<<<< HEAD
            'lo_publicstakeholdertablepanel checkbox[itemId="showPendingStakeholdersCheckbox"]': {
                change: this.onShowPendingStakeholdersCheckboxChange
=======
            'lo_publicstakeholdertablepanel button[itemId=stakeholderDeleteAllFiltersButton]': {
                click: this.onStakeholderDeleteAllFiltersButtonClick
            },
            'gridpanel[itemId=activityGrid] gridcolumn[name=yearofinvestmentcolumn]': {
                afterrender: this.onActivityYearColumnAfterrender
            },
            'gridpanel[itemId=activityGrid] gridcolumn[name=activityCountryColumn]': {
                afterrender: this.onActivityCountryColumnAfterrender
            },
            'gridpanel[itemId=stakeholderGrid] gridcolumn[name=stakeholdernamecolumn]': {
                afterrender: this.onStakeholderNameColumnAfterrender
            },
            'gridpanel[itemId=stakeholderGrid] gridcolumn[name=stakeholdercountrycolumn]': {
                afterrender: this.onStakeholderCountryColumnAfterrender
>>>>>>> b33bd569272e76068610f61b46170f8031a005f6
            }
        });
    },

    /**
     * Adds a beforeload action to the ActivityGridStore to filter the activites
     * according to the current map extent.
     * The checkbox to toggle the spatial filter is not available anymore, the
     * GridStore is always bound to the map extent.
     */
    onActivityTablePanelRender: function() {

        // Adds a beforeload action
        this.getActivityGridStore().on('beforeload', function(store){

            // Get the store proxy
            var proxy = store.getProxy();
            // Get the map view.
            var map = this.getMapPanel().getMap();
            // Get the extent if the map is already initialized, else the
            // map extent is still null
            if(map.getExtent()){
                // Set the bounding box as extra parameter
                proxy.setExtraParam("bbox", map.getExtent().toBBOX());
            }

            // Check if pending changes are requested
            if(this.getShowPendingActivitiesCheckbox()){
                this.getShowPendingActivitiesCheckbox().getValue() ?
                proxy.setExtraParam('status', 'pending') : proxy.setExtraParam('status', null);
            }
        }, this);
    },

    onStakeholderTablePanelRender: function(comp) {
        this.getStakeholderGridStore().on('beforeload', function(store)  {
            var proxy = store.getProxy();
            if(this.getShowPendingStakeholdersCheckbox()){
                this.getShowPendingStakeholdersCheckbox().getValue() ?
                proxy.setExtraParam('status', 'pending') : proxy.setExtraParam('status', null);
            }
        }, this);

        // Update filter count
        this._updateFilterCount();

        // If logged in, add a button to add new Activity
        if (Lmkp.toolbar != false) {
            var tb = this.getActivityGridTopToolbar();
            if (tb) {
                tb.insert(0, {
                    text: 'Add new Activity',
                    itemId: 'newActivityButton'
                });
            }
        }
    },

    /**
     * Reloads the Activities grid whenever the checkbox to show or hide activites
     * with pending changes is checked or unchecked.
     */
    onShowPendingActivitiesCheckboxChange: function(field, newValue, oldValue){
        this.getActivityGridStore().load();
    },

    /**
     * Reloads the Stakeholders grid whenever the checkbox to show or hide activites
     * with pending changes is checked or unchecked.
     */
    onShowPendingStakeholdersCheckboxChange: function(field, newValue, oldValue){
        this.getStakeholderGridStore().load();
    },

    onActivityDetailWindowBeforeShow: function(comp){
        var proxy = comp.getHistoryStore().getProxy();
        this.getShowPendingActivitiesCheckbox().getValue?
        // Show all versions with any status
        proxy.setExtraParam('status', 'pending,active,inactive,deleted,rejected,edited') :
        // else show only active and inactive versions
        proxy.setExtraParam('status', '')
    },

    /**
     * Change selection in other grid when a row is selected. Also highlight
     * feature on map (only for Activities?)
     */
    onTableSelectionChange: function(model, selected) {
    	
        if (selected && selected.length > 0) {
            var sel = selected[0];
    		
            // Activity or Stakeholder?
            var otherStore = null;
            if (sel.modelName == 'Lmkp.model.Stakeholder') {
                otherStore = this.getActivityGridStore();
            } else if (sel.modelName == 'Lmkp.model.Activity') {
                otherStore = this.getStakeholderGridStore();
            }
            
            if (otherStore) {
                // Update other grid panel
                otherStore.syncByOtherId(sel.get('id'));
            }

            // If Activity was selected, also show Feature on map
            if (sel.modelName == 'Lmkp.model.Activity') {
                var mapController = this.getController('public.Map');
                mapController.showActivityOnMap(sel);
            }
        }
    },

    /**
     * Show details of selected item in popup window.
     */
    onShowDetailsColumnClick: function(grid) {
        var record = grid.getSelectionModel().getSelection()[0];

        if (record) {

            // Activity or Stakeholder?
            var type = null;
            if (record.modelName == 'Lmkp.model.Stakeholder') {
                type = 'stakeholder';
            } else if (record.modelName == 'Lmkp.model.Activity') {
                type = 'activity';
            }

            var w;

            if (type == 'activity') {
                // Show details window
                w = Ext.create('Lmkp.view.activities.Details',{
                    activity: record
                }).show();
                w._collapseHistoryPanel();
            } else if (type == 'stakeholder') {
                // Show details window
                w = Ext.create('Lmkp.view.stakeholders.Details',{
                    stakeholder: record
                }).show();
                w._collapseHistoryPanel();
            }
        }
    },
    
    onNewActivityButtonClick: function() {
    	// Create and load a store with all mandatory keys
        var mandatoryStore = Ext.create('Lmkp.store.ActivityConfig');
        mandatoryStore.filter('allowBlank', false);
        mandatoryStore.load(function() {
            // Create and load a second store with all keys
            var completeStore = Ext.create('Lmkp.store.ActivityConfig');
            completeStore.load(function() {
                // When loaded, create panel and show window
                var panel = Ext.create('Lmkp.view.activities.NewActivity');
                panel.showForm(mandatoryStore, completeStore);
		    	var win = Ext.create('Ext.window.Window', {
		    		autoScroll: true,
		    		modal: true,
		    		items: [panel]
		    	});
		    	win.show();
            });
        });
    },

    /**
     * Nicely render 'Country' column of Activity grid.
     */
    onActivityCountryColumnAfterrender: function(comp) {
        this._renderColumnMultipleValues(comp, "activity-attr_country");
    },

    /**
     * Nicely render 'Year of Investment' column of Activity grid. Value '0' is
     * treated as null
     */
    onActivityYearColumnAfterrender: function(comp) {
        this._renderColumnMultipleValues(comp, "activity-attr_yearofinvestment",
        [0]);
    },

    /**
     * Nicely render 'Name' column of Stakeholder grid.
     */
    onStakeholderNameColumnAfterrender: function(comp) {
        this._renderColumnMultipleValues(comp, "stakeholder-attr_name");
    },

    /**
     * Nicely render 'Country' column of Stakeholder grid.
     */
    onStakeholderCountryColumnAfterrender: function(comp) {
        this._renderColumnMultipleValues(comp, "stakeholder-attr_country");
    },

    onActivityFilterButtonClick: function() {
        // Only create window once
        var q = Ext.ComponentQuery.query('lo_filteractivitywindow');
        var win = q.length > 0 ? q[0] : Ext.create('Lmkp.view.public.FilterActivityWindow');
        // Update filter count when filters are modified
        var me = this;
        win.on('filterEdited', function() {
            me._updateFilterCount('activities');
        });
        win.show();
    },

    onStakeholderFilterButtonClick: function() {
        // Only create window once
        var q = Ext.ComponentQuery.query('lo_filterstakeholderwindow');
<<<<<<< HEAD
        var win = q.length > 0 ? q[0] : Ext.create('Lmkp.view.public.FilterStakeholderWindow');
        ;
=======
        var win = q.length > 0 ? q[0] : Ext.create('Lmkp.view.public.FilterStakeholderWindow');;
        // Update filter count when filters are modified
        var me = this;
        win.on('filterEdited', function() {
            me._updateFilterCount('stakeholders');
        });
>>>>>>> b33bd569272e76068610f61b46170f8031a005f6
        win.show();
    },

    onClearSelectionButtonClick: function() {

        // Reload ActivityGrid. Use the filter controller in order to keep
        // results filtered
        var filterController = this.getController('public.Filter');
        filterController.applyFilter();
    },

    onActivityDeleteAllFiltersButtonClick: function() {
        var q = Ext.ComponentQuery.query('lo_editoractivityfilterpanel');
        var filterPanel = q.length > 0 ? q[0] : null;
        if (filterPanel) {
            // Delete all filter items
            var filterItems = filterPanel.query('lo_itemsfilterpanel');
            for (var i in filterItems) {
                filterItems[i].destroy();
            }
            // Reapply filter
            var filterController = this.getController('public.Filter');
            filterController.applyFilter(true);
            this._updateFilterCount('activities');
        }
    },

    onStakeholderDeleteAllFiltersButtonClick: function() {
        var q = Ext.ComponentQuery.query('lo_editorstakeholderfilterpanel');
        var filterPanel = q.length > 0 ? q[0] : null;
        if (filterPanel) {
            // Delete all filter items
            var filterItems = filterPanel.query('lo_itemsfilterpanel');
            for (var i in filterItems) {
                filterItems[i].destroy();
            }
            // Reapply filter
            var filterController = this.getController('public.Filter');
            filterController.applyFilter(true);
            this._updateFilterCount('stakeholders');
        }
    },

    /**
     * Helper function to find values inside Tags and TagGroups.
     * 'ignored': Optionally provide an array of (dummy) values to be ignored.
     */
    _renderColumnMultipleValues: function(comp, dataIndex, ignored) {
        var me = this;
        comp.renderer = function(value, p, record) {
            // loop through all tags is needed
            var taggroupStore = record.taggroups();
            var ret = [];
            taggroupStore.each(function(taggroup) {
                var tagStore = taggroup.tags();
                tagStore.each(function(tag) {
                    if (tag.get('key') == Lmkp.ts.msg(dataIndex)) {
                        if (!ignored || !me._isInArray(ignored, tag.get('value'))) {
                            ret.push(Ext.String.format('{0}', tag.get('value')));
                        }
                    }
                });
            });
            if (ret.length > 0) {
                return ret.join(', ');
            } else {
                return Lmkp.ts.msg("unknown");
            }
        }
    },

    _isInArray: function(arr, obj) {
        for(var i=0; i<arr.length; i++) {
            if (arr[i] == obj) return true;
        }
    },

    /**
     * Update the filter buttons to show the count of currently active filters.
     * {items}: Optional identifier ('activities' or 'stakeholders') to update
     * only one button.
     */
    _updateFilterCount: function(items) {

        if (!items || items == 'activities') {
            // Activities
            var aToolbar = this.getActivityGridTopToolbar();
            var aItemId = 'activity';
            var aCount = this.getActivityTablePanel().getFilterCount();
            __updateButton(aToolbar, aItemId, aCount);
        }

        if (!items || items == 'stakeholders') {
            // Stakeholders
            var shToolbar = this.getStakeholderGridTopToolbar();
            var shItemId = 'stakeholder';
            var shCount = this.getStakeholderTablePanel().getFilterCount();
            __updateButton(shToolbar, shItemId, shCount);
        }

        function __updateButton(toolbar, itemId, count) {
            // Update button showing count
            var button = toolbar.down('button[itemId=' + itemId + 'FilterButton]');
            if (button) {
                // Remove old button
                toolbar.remove(button);
            }
            if (toolbar && count != null) {
                // Create new button
                var newbutton = Ext.create('Ext.button.Button', {
                    text: 'Filter (' + count + ' active)',
                    itemId: itemId + 'FilterButton'
                });
                toolbar.add(newbutton);
            }
            // Also enable/disable button to delete all filters
            var deleteButton = toolbar.down('button[itemId=' + itemId + 'DeleteAllFiltersButton]');
            if (deleteButton) {
                deleteButton.setDisabled(count == 0);
            }
        }
    }
});
