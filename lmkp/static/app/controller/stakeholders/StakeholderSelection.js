Ext.define('Lmkp.controller.stakeholders.StakeholderSelection', {
    extend: 'Ext.app.Controller',

    refs: [{
        ref: 'stakeholderSelection',
        selector: 'lo_stakeholderselection'
    }],

    views: [
    'stakeholders.StakeholderSelection'
    ],

    init: function(){
        this.control({
            'lo_stakeholderselection combo[itemId="searchTextfield"]': {
                select: this.onSearchSelect
            },
            'lo_stakeholderselection button[itemId="clearButton"]':{
                click: this.onClearButtonClick
            },
            'lo_stakeholderselection button[itemId="confirmButton"]': {
                click: this.onConfirmButtonClick
            }
        });
    },

    onSearchSelect: function(combo, records, eOpts){
        this.getStakeholderSelection().confirmButton.setText("Select Stakeholder");
        
        var p = Ext.create('Lmkp.view.stakeholders.StakeholderPanel',{
            contentItem: records[0],
            region: 'south'
        });

        this.getStakeholderSelection().setSouthPanel(p);
        this.getStakeholderSelection().add(p);

    },

    onClearButtonClick: function(button, event, eOpts){

        var sel = this.getStakeholderSelection();

        var p = sel.getSouthPanel();
        sel.remove(p);
        sel.setSouthPanel(null);

        sel.getConfirmButton().setText("Add new Stakeholder");

        sel.down('combo[itemId="searchTextfield"]').setValue(null);
    },

    onConfirmButtonClick: function(button, event, eOpts){
        var sel = this.getStakeholderSelection();

        if(sel.getSouthPanel()){
            var contentItem = sel.getSouthPanel().contentItem;
            sel.setSelectedStakeholder(contentItem);
            sel.close();
        } else {
            var w = Ext.create('Lmkp.view.stakeholders.NewStakeholder');
            w.on('close', function(panel, eOpts){
                sel.setSelectedStakeholder(panel.getAddedStakeholder());
                sel.close();
            }, this);
            w.show();
        //            w.on('close', function(panel, eOpts){
        //                sel.close();
        //            });
        }

    }

});