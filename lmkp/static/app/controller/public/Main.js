Ext.define('Lmkp.controller.public.Main', {
    extend: 'Ext.app.Controller',

    refs: [{
        ref: 'mapPanel',
        selector: 'lo_publicmappanel'
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
            'lo_publicactivitytablepanel gridpanel[itemId=activityGrid]': {
                selectionchange: this.onTableSelectionChange
            },
            'lo_publicactivitytablepanel gridpanel templatecolumn[name=showDetailsColumn]': {
                click: this.onShowDetailsColumnClick
            },
            'gridpanel[itemId=activityGrid] gridcolumn[name=activityCountryColumn]': {
                afterrender: this.onActivityCountryColumnAfterrender
            },
            'gridpanel[itemId=activityGrid] gridcolumn[name=yearofinvestmentcolumn]': {
                afterrender: this.onActivityYearColumnAfterrender
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
            'lo_publicstakeholdertablepanel button[itemId=stakeholderFilterButton]': {
                click: this.onStakeholderFilterButtonClick
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
                // Actually this is bad coding style! This should be done in a
                // superior controller ...
                var map = this.getMapPanel().getMap();
                // Get the extent if the map is already initialized, else the
                // map extent is still null
                if(map.getExtent()){
                    // Set the bounding box as extra parameter
                    proxy.setExtraParam("bbox", map.getExtent().toBBOX());
                }
        }, this);
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

            if (type) {
            	// Show details
            	console.log("Coming soon: Details for: " + type);
            	console.log(record);
            }
    	}
    },

    /**
     * Nicely render 'Country' column of Activity grid.
     */
    onActivityCountryColumnAfterrender: function(comp) {
        this._renderColumnMultipleValues(comp, "activity-attr_country");
    },

    /**
     * Nicely render 'Year of Investment' column of Activity grid.
     */
    onActivityYearColumnAfterrender: function(comp) {
        this._renderColumnMultipleValues(comp, "activity-attr_yearofinvestment");
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
        console.log("popup with filters for activities coming soon.");
    },

    onStakeholderFilterButtonClick: function() {
        console.log("popup with filters for stakeholders coming soon.");
    },

    /**
     * Helper function to find values inside Tags and TagGroups.
     */
    _renderColumnMultipleValues: function(comp, dataIndex) {
        comp.renderer = function(value, p, record) {
            // loop through all tags is needed
            var taggroupStore = record.taggroups();
            var ret = [];
            for (var i=0; i<taggroupStore.count(); i++) {
                var tagStore = taggroupStore.getAt(i).tags();
                for (var j=0; j<tagStore.count(); j++) {
                    if (tagStore.getAt(j).get('key') == Lmkp.ts.msg(dataIndex)) {
                        ret.push(Ext.String.format('{0}', tagStore.getAt(j).get('value')));
                    }
                }
            }
            if (ret.length > 0) {
                return ret.join(', ');
            } else {
                return Lmkp.ts.msg("unknown");
            }
        }
    }
});
