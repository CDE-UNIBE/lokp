Ext.define('Lmkp.controller.activities.NewActivityWindow', {
    extend: 'Ext.app.Controller',

    refs: [{
        ref: 'newActivityWindow',
        selector: 'lo_newactivitywindow'
    },{
        ref: 'selectStakeholderFieldSet',
        selector: 'lo_newactivitywindow fieldset[itemId="selectStakeholderFieldSet"]'
    }],

    views: [
    'activities.NewActivityWindow'
    ],

    init: function(){
        this.control({
            'lo_newactivitywindow button[itemId="selectStakeholderButton"]': {
                click: this.onButtonClick
            }
        });
    },

    onButtonClick: function(button, event){
        var sel = Ext.create('Lmkp.view.stakeholders.StakeholderSelection');

        var w = this.getNewActivityWindow();

        sel.on('close', function(panel, eOpts){
            var sh = panel.getSelectedStakeholder();
            this.getSelectStakeholderFieldSet().add({
                stakeholder: sh,
                xtype: 'lo_stakeholderfieldcontainer'
            });
        }, this);
        sel.show();
    }

});