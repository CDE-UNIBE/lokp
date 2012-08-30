Ext.define('Lmkp.controller.editor.Overview', {
    extend: 'Ext.app.Controller',

    refs: [{
        ref: 'mapPanel',
        selector: 'lo_editormappanel'
    }, {
        ref: 'detailPanel',
        selector: 'lo_editordetailpanel'
    },{
        ref: 'newActivityPanel',
        selector: 'lo_newactivitypanel'
    },{
        ref: 'selectStakeholderFieldSet',
        selector: 'lo_newactivitypanel fieldset[itemId="selectStakeholderFieldSet"]'
    }],

    requires: [
    'Lmkp.model.Activity',
    'Lmkp.model.TagGroup',
    'Lmkp.model.Tag',
    'Lmkp.model.MainTag',
    'Lmkp.model.Point'
    ],

    stores: [
    'ActivityGrid',
    'ActivityConfig',
    'StakeholderGrid',
    'StakeholderConfig',
    'Profiles'
    ],

    views: [
    'editor.Detail',
    'editor.Map',
    'activities.Details',
    'activities.History',
    'activities.Filter',
    'stakeholders.StakeholderSelection',
    'items.FilterPanel'
    ],

    init: function() {
        // Get the config stores and load them
        this.getActivityConfigStore().load();
        this.getStakeholderConfigStore().load();

        this.control({
            'lo_editortablepanel': {
            //render: this.onTablePanelRender
            },
            'lo_editormappanel': {
                render: this.onMapPanelRender
            }
        });
    }
});
