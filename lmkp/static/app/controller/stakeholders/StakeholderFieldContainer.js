Ext.define('Lmkp.controller.stakeholders.StakeholderFieldContainer', {
    extend: 'Ext.app.Controller',

    views: [
    'stakeholders.StakeholderFieldContainer'
    ],

    init: function(){
        this.control({
            'lo_stakeholderfieldcontainer button': {
                click: this.onButtonClick
            }
        });
    },

    onButtonClick: function(button, event){


        var parentFieldSet = button.up('fieldset');
        parentFieldSet.add({
            xtype: 'lo_stakeholderfieldcontainer'
        });

        // disable button if clicked
        button.disable();
    }

});