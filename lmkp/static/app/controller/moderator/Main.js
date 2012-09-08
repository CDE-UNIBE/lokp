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
            },
            'lo_moderatorreviewpanel button[itemId="reviewSubmitButton"]': {
                click: this.onReviewSubmitButton
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
        // Set initial proxy (this makes sure to delete all reference to 
        // stakeholders and adds/removes parameter to show/hide pending)
        this.getActivityGridStore().setInitialProxy();
        this.getActivityGridStore().loadPage(1);
        // Syncronize with the checkbox above the stakeholder grid.
        // Unregister first the load event to prevent an endless loop.
        var cb = this.getPendingStakeholdersCheckbox();
        cb.un('load', this.onPendingStakeholdersCheckboxChange);
        cb.setValue(field.getValue());
        cb.on('load', this.onPendingStakeholdersCheckboxChange);
    },

    /**
     * Reloads the Stakeholders grid whenever the checkbox to show or hide activites
     * with pending changes is checked or unchecked.
     */
    onPendingStakeholdersCheckboxChange: function(field, newValue, oldValue){
        // Set initial proxy (this makes sure to delete all reference to 
        // activities and adds/removes parameter to show/hide pending)
        this.getStakeholderGridStore().setInitialProxy();
        this.getStakeholderGridStore().loadPage(1);
        // Syncronize with the checkbox above the activity grid.
        // Unregister first the load event to prevent an endless loop.
        var cb = this.getPendingActivitiesCheckbox();
        cb.un('load', this.onPendingActivitiesCheckboxChange);
        cb.setValue(field.getValue());
        cb.on('load', this.onPendingActivitiesCheckboxChange);
    },

    onReviewSubmitButton: function(btn){

        var mapPanel = this.getMapPanel();

        btn.up('form').submit({
            failure: function(form, response) {
                var msg = 'Request failed.<br/>Server response: ';
                msg += response.response.status + ' ' + response.response.statusText;
                Ext.Msg.show({
                    buttons: Ext.Msg.CANCEL,
                    icon: Ext.Msg.ERROR,
                    msg: msg,
                    scope: this,
                    title: 'Failed'
                });
            },
            scope: btn.up('window'),
            success: function(form, response) {
                var returnJson = Ext.decode(response.response.responseText);
                if(returnJson.success){
                    Ext.Msg.show({
                        buttons: Ext.Msg.OK,
                        fn: function(buttonId, text, opt){
                            this.close();
                        },
                        icon: Ext.Msg.INFO,
                        msg: returnJson.msg,
                        scope: this,
                        title: 'Success'
                    });
                    // If the review was successful it is necessary to reload
                    // the ActivityVector store
                    mapPanel.getVectorStore().load();
                } else {
                    Ext.Msg.show({
                        buttons: Ext.Msg.CANCEL,
                        icon: Ext.Msg.ERROR,
                        msg: returnJson.msg,
                        scope: this,
                        title: 'Failed'
                    });
                }
            }
        });

        
    }

});