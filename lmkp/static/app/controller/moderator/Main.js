Ext.define('Lmkp.controller.moderator.Main', {
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
            'lo_activitydetailwindow': {
                beforeshow: this.onActivityDetailWindowBeforeShow
            }
        });
    }
});