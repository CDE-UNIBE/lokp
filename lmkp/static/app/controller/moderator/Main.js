Ext.define('Lmkp.controller.moderator.Main', {
    extend: 'Ext.app.Controller',

    refs: [{
        ref: 'mapPanel',
        selector: 'lo_publicmappanel'
    },{
        ref: 'pendingActivitiesCheckbox',
        selector: 'lo_publicactivitytablepanel checkbox[itemId="pendingActivitiesCheckbox"]'
    },{
        ref: 'pendingStakeholdersCheckbox',
        selector: 'lo_publicstakeholdertablepanel checkbox[itemId="pendingStakeholdersCheckbox"]'
    }],

    stores: [
    'ActivityGrid',
    'ActivityConfig',
    'StakeholderGrid',
    'StakeholderConfig'
    ],

    init: function() {
        // Get the config stores and load them
        this.getActivityConfigStore().load();
        this.getStakeholderConfigStore().load();

        this.control({
            'lo_publicactivitytablepanel': {
                beforerender: this.onActivityTablePanelBeforeRender,
                render: this.onActivityTablePanelRender
            },
            'lo_publicstakeholdertablepanel': {
                beforerender: this.onStakeholderTablePanelBeforeRender,
                render: this.onStakeholderTablePanelRender
            },
            'lo_activitydetailwindow': {
                beforeshow: this.onActivityDetailWindowBeforeShow
            },
            'lo_stakeholderdetailwindow': {
                beforeshow: this.onStakeholderDetailWindowBeforeShow
            },
            'lo_publicstakeholdertablepanel checkbox[itemId="pendingStakeholdersCheckbox"]': {
                change: this.onPendingStakeholdersCheckboxChange
            },
            'lo_publicactivitytablepanel checkbox[itemId="pendingActivitiesCheckbox"]': {
                change: this.onPendingActivitiesCheckboxChange
            }
        });
    },

    /**
     * Insert a checkbox to show pending Activity changes
     */
    onActivityTablePanelBeforeRender: function(comp) {
        var pendingCheckbox = Ext.create('Ext.form.Checkbox',{
            checked: true,
            boxLabel: 'Show pending changes',
            itemId: 'pendingActivitiesCheckbox'
        });
        var tbar = comp.down('[id="activityGridTopToolbar"]');
        tbar.insert(1, pendingCheckbox);
    },

    /**
     * Add a beforeload listener to the ActivityGrid store to check if
     * pending changes needs to be requested.
     */
    onActivityTablePanelRender: function(comp) {
        // Adds a beforeload action
        this.getActivityGridStore().on('beforeload', function(store){
            // Get the store proxy
            var proxy = store.getProxy();
            // Check if pending changes are requested
            if(this.getPendingActivitiesCheckbox()){
                this.getPendingActivitiesCheckbox().getValue() ?
                proxy.setExtraParam('status', 'pending') : proxy.setExtraParam('status', null);
            }
        }, this);
    },

    onStakeholderTablePanelBeforeRender: function(comp) {
        var checkbox = Ext.create('Ext.form.Checkbox', {
            checked: true,
            boxLabel: 'Show pending changes',
            itemId: 'pendingStakeholdersCheckbox'
        });
        var tbar = comp.down('[id="stakeholderGridTopToolbar"]');
        tbar.insert(1, checkbox);
    },

    onStakeholderTablePanelRender: function(comp) {
        // Adds a beforeload action
        this.getStakeholderGridStore().on('beforeload', function(store){
            // Get the store proxy
            var proxy = store.getProxy();
            // Check if pending changes are requested
            if(this.getPendingStakeholdersCheckbox()){
                this.getPendingStakeholdersCheckbox().getValue() ?
                proxy.setExtraParam('status', 'pending') : proxy.setExtraParam('status', null);
            }
        }, this);
    },

    onActivityDetailWindowBeforeShow: function(comp){
        var proxy = comp.getHistoryStore().getProxy();
        this.getPendingActivitiesCheckbox().getValue?
        // Show all versions with any status
        proxy.setExtraParam('status', 'pending,active,inactive,deleted,rejected,edited') :
        // else show only active and inactive versions
        proxy.setExtraParam('status', '');
    },

    onStakeholderDetailWindowBeforeShow: function(comp){
        var proxy = comp.getHistoryStore().getProxy();
        this.getPendingStakeholdersCheckbox().getValue?
        // Show all versions with any status
        proxy.setExtraParam('status', 'pending,active,inactive,deleted,rejected,edited') :
        // else show only active and inactive versions
        proxy.setExtraParam('status', '');
    },

    /**
     * Reloads the Activities grid whenever the checkbox to show or hide activites
     * with pending changes is checked or unchecked.
     */
    onPendingActivitiesCheckboxChange: function(field, newValue, oldValue){
        this.getActivityGridStore().load();
    },

    /**
     * Reloads the Stakeholders grid whenever the checkbox to show or hide activites
     * with pending changes is checked or unchecked.
     */
    onPendingStakeholdersCheckboxChange: function(field, newValue, oldValue){
        this.getStakeholderGridStore().load();
    }

});