Ext.define('Lmkp.controller.stakeholders.StakeholderSelection', {
    extend: 'Ext.app.Controller',

    refs: [{
        ref: 'stakeholderSelection',
        selector: 'lo_stakeholderselection'
    }],

    views: [
    'stakeholders.StakeholderSelection',
    'stakeholders.NewStakeholder'
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
        var sel  = this.getStakeholderSelection();
        sel.confirmButton.setText("Select Stakeholder");
        
        var p = Ext.create('Lmkp.view.stakeholders.StakeholderPanel', {
            contentItem: records[0],
            editable: false,
            region: 'south'
        });

        // Remove first the southern panel if there is any
        if(sel.getSouthPanel()){
            sel.remove(sel.getSouthPanel());
        }

        sel.setSouthPanel(p);
        sel.add(p);
        sel.doLayout();
    },

    onClearButtonClick: function(button, event, eOpts){

        var sel = this.getStakeholderSelection();

        var p = sel.getSouthPanel();
        if (p) {
            sel.remove(p);
            sel.setSouthPanel(null);
        }

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
            var w = Ext.create('Ext.window.Window', {
                height: 240,
                width: 400,
                layout: 'border',
                items: [{
                    autoScroll: true,
                    region: 'center',
                    xtype: 'lo_newstakeholderpanel'
                }],
                title: 'Add new Stakeholder'
            });
            w.on('close', function(window, eOpts){
                this.onSearchSelect(
                    window.down('combo[itemId="searchTextfield"]'),
                    [window.down('lo_newstakeholderpanel').getAddedStakeholder()]);
            }, this);
            w.show();
        }

    }

});