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

    // Make the public.Map controller available in the whole instance
    mapController: null,

    init: function() {
        // Get the config stores and load them
        this.getActivityConfigStore().load();
        this.getStakeholderConfigStore().load();

        this.mapController = this.getController('public.Map');

        this.control({
            'lo_publicactivitytablepanel': {
                render: this.onActivityTablePanelRender
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
            'lo_publicstakeholdertablepanel button[itemId=stakeholderFilterButton]': {
                click: this.onStakeholderFilterButtonClick
            },
            'lo_publicstakeholdertablepanel button[itemId=stakeholderResetSelectionButton]': {
                click: this.onClearSelectionButtonClick
            },
            'lo_publicstakeholdertablepanel button[itemId=stakeholderDeleteAllFiltersButton]': {
                click: this.onStakeholderDeleteAllFiltersButtonClick
            },
            'gridpanel[itemId=activityGrid] gridcolumn[name=yearofinvestmentcolumn]': {
                afterrender: this.onActivityYearColumnAfterrender
            },
            'gridpanel[itemId=activityGrid] gridcolumn[name=activityCountryColumn]': {
                afterrender: this.onActivityCountryColumnAfterrender
            },
            'gridpanel[itemId=activityGrid] gridcolumn[name=activitySizeColumn]': {
                afterrender: this.onActivitySizeColumnAfterrender
            },
            'gridpanel[itemId=stakeholderGrid] gridcolumn[name=stakeholdernamecolumn]': {
                afterrender: this.onStakeholderNameColumnAfterrender
            },
            'gridpanel[itemId=stakeholderGrid] gridcolumn[name=stakeholdercountrycolumn]': {
                afterrender: this.onStakeholderCountryColumnAfterrender
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

        var grid = this.getActivityTablePanel();
        var store = this.getActivityGridStore();
        
        // Adds a beforeload action
        store.on('beforeload', function(store){

            // Loading mask
            grid.setLoading({msg: Lmkp.ts.msg('gui_loading')});

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
        }, this);

        store.on('load', function() {
            // Loading mask
            grid.setLoading(false);
        });

    },

    onStakeholderTablePanelRender: function(comp) {

        var grid = this.getStakeholderTablePanel();
        var store = this.getStakeholderGridStore();

        // Loading mask
        store.on('beforeload', function() {
            grid.setLoading({msg: Lmkp.ts.msg('gui_loading')});
        });
        store.on('load', function() {
            grid.setLoading(false);
        });

        // Update filter count
        this._updateFilterCount();

        // If logged in, add a button to add new Activity
        if (Lmkp.editor) {
            var tb = this.getActivityGridTopToolbar();
            if (tb) {
                tb.insert(0, {
                    text: Lmkp.ts.msg('activities_add-new-activity'),
                    itemId: 'newActivityButton'
                });
            }
        }

        //this.getStakeholderGridStore().on('load', this._reloadActivityGridStore, this);
    },

    /**
     *
     *
    _reloadStakeholderGridStore: function(store, records, successful, eOpts){
        var extraParams = store.getProxy().extraParams;
        this.getStakeholderGridStore().un('load', this._reloadActivityGridStore, this);
        this.getStakeholderGridStore().syncWithActivities(extraParams);
        this.getStakeholderGridStore().on('load', this._reloadActivityGridStore, this);
    },

    _reloadActivityGridStore: function(store, records, successful, eOpts){
        var extraParams = store.getProxy().extraParams;
        this.getActivityGridStore().un('load', this._reloadStakeholderGridStore, this);
        this.getActivityGridStore().syncWithStakeholders(extraParams);
        this.getActivityGridStore().on('load', this._reloadStakeholderGridStore, this);
    },
     */

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

            // Show Feature on the map
            this.mapController.selectActivity(sel);
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

                // Show Feature on the map
                this.mapController.selectActivity(record);
                
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
        var me = this;
        var infoWindow = Ext.create('Lmkp.utils.MessageBox');
        infoWindow.alert(
            Lmkp.ts.msg('activities_new-title'),
            Lmkp.ts.msg('activities_new-step-1'),
            function() {
                var editorMapController = me.getController('editor.Map');
                editorMapController.clickAddLocationButton();
            }
            );
    },

    /**
     * Nicely render 'Country' column of Activity grid.
     */
    onActivityCountryColumnAfterrender: function(comp) {
        this._renderColumnMultipleValues(comp, 'activity_db-key-country');
    },

    /**
     * Nicely render 'Year of Investment' column of Activity grid. Value '0' is
     * treated as null
     */
    onActivityYearColumnAfterrender: function(comp) {
        this._renderColumnMultipleValues(comp, 'activity_db-key-yearofagreement');
    },
    
    /**
     * Nicely render 'Size' column of Activity grid.
     */
    onActivitySizeColumnAfterrender: function(comp) {
        this._renderColumnMultipleValues(comp, 'activity_db-key-contractarea')
    },

    /**
     * Nicely render 'Name' column of Stakeholder grid.
     */
    onStakeholderNameColumnAfterrender: function(comp) {
        this._renderColumnMultipleValues(comp, 'stakeholder_db-key-name');
    },

    /**
     * Nicely render 'Country' column of Stakeholder grid.
     */
    onStakeholderCountryColumnAfterrender: function(comp) {
        this._renderColumnMultipleValues(comp, 'stakeholder_db-key-country');
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
        var win = q.length > 0 ? q[0] : Ext.create('Lmkp.view.public.FilterStakeholderWindow');
        ;
        // Update filter count when filters are modified
        var me = this;
        win.on('filterEdited', function() {
            me._updateFilterCount('stakeholders');
        });
        win.show();
    },

    onClearSelectionButtonClick: function() {

        // Reload ActivityGrid. Use the filter controller in order to keep
        // results filtered
        var filterController = this.getController('public.Filter');
        filterController.applyFilter();

        //
        this.mapController.unselectAll();
    },

    onActivityDeleteAllFiltersButtonClick: function() {
        var q = Ext.ComponentQuery.query('lo_activityfilterpanel');
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
        var q = Ext.ComponentQuery.query('lo_stakeholderfilterpanel');
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
        
        comp.renderer = function(value, metaData, record) {

            // Check the current status of the record and add accordingly an
            // additional class to the td element
            if(record.get("status") == Lmkp.ts.msg('status_pending')){
                metaData.tdCls = "status-pending";
            }

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
                return Lmkp.ts.msg('gui_unknown');
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
                    //                    text: 'Filter (' + count + ' active)',
                    text: Lmkp.ts.msg('gui_filter-count').replace('{0}', count),
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
