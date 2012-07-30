Ext.define('Lmkp.controller.activities.NewActivity', {
    extend: 'Ext.app.Controller',

    refs: [{
        ref: 'newActivityPanel',
        selector: 'lo_newactivitypanel'
    },{
        ref: 'selectStakeholderFieldSet',
        selector: 'lo_newactivitypanel fieldset[itemId="selectStakeholderFieldSet"]'
    }],

    views: [
    'activities.NewActivity'
    ],

    init: function(){
        this.control({
            'lo_newactivitypanel button[itemId="selectStakeholderButton"]': {
                click: this.onStakeholderButtonClick
            }
        });
    },

    onStakeholderButtonClick: function(button, event){
        var sel = Ext.create('Lmkp.view.stakeholders.StakeholderSelection');

        var w = this.getNewActivityPanel();

        sel.on('close', function(panel, eOpts){
            var sh = panel.getSelectedStakeholder();
            this.getSelectStakeholderFieldSet().insert(
                0, {
                    stakeholder: sh,
                    xtype: 'lo_stakeholderfieldcontainer'
                });
        }, this);
        sel.show();
    }

});