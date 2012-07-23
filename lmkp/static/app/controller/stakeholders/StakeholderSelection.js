Ext.define('Lmkp.controller.stakeholders.StakeholderSelection', {
    extend: 'Ext.app.Controller',

    views: [
    'stakeholders.StakeholderSelection'
    ],

    init: function(){
        this.control({
            'lo_stakeholderselection combo[itemId=Name__textfield]': {
                select: this.onNameSelect
            }
        });
    },

    onNameSelect: function(combo, records, eOpts){
        console.log(records[0]);

        

    }

});