Ext.define('Lmkp.controller.moderator.Details', {
    extend: 'Ext.app.Controller',

    models: [],

    refs: [{
        ref: 'activityDetailWindow',
        selector: 'lo_activitydetailwindow'
    },{
        ref: 'stakeholderDetailWindow',
        selector: 'lo_stakeholderdetailwindow'
    },{
        ref: 'activityDetailWizardPanel',
        selector: 'lo_activitydetailwindow panel[itemId="activityDetailWizardPanel"]'
    }],

    requires: [],

    stores: [],

    views: [
    'activities.Details',
    'activities.Filter',
    'moderator.Review'
    ],

    init: function() {
        this.control({
            'lo_activitydetailwindow panel[itemId="activityDetailWizardPanel"]': {
                render: this.onActivityDetailCenterPanelRender
            },
            'lo_stakeholderdetailwindow panel[itemId="stakeholderDetailWizardPanel"]': {
                render: this.onStakeholderDetailCenterPanelRender
            }
        });
    },

    onActivityDetailCenterPanelRender: function(comp){

        var store = this.getActivityDetailWindow().getHistoryStore();

        var toolbar = comp.down('toolbar[dock="bottom"]');
        toolbar ? comp.remove(toolbar) : null;

        store.on('load', function(store, records, successful){

            if(store.first().get('status') == 'pending'){

                var panel = Ext.create('Lmkp.view.moderator.Review',{
                    itemId: 'reviewPanel',
                    store: store,
                    type: 'activities'
                });

                comp.add(panel);
            
                var prevButton = Ext.create('Ext.button.Button',{
                    disabled: true,
                    itemId: 'card-prev',
                    handler: function(btn) {
                        var layout = comp.getLayout();
                        if(layout.getPrev()){
                            layout.setActiveItem(layout.getPrev());
                        }
                        btn.setDisabled(!layout.getPrev());
                        nextButton.setDisabled(!layout.getNext());
                    },
                    text: '&laquo; Back'
                });

                var nextButton = Ext.create('Ext.button.Button',{
                    itemId: 'card-next',
                    handler: function(btn){
                        var layout = comp.getLayout();
                        if(layout.getNext()){
                            layout.setActiveItem(layout.getNext());
                        }
                        btn.setDisabled(!layout.getNext());
                        prevButton.setDisabled(!layout.getPrev());
                    },
                    text: 'Review pending changes &raquo;'
                });
            
                toolbar = Ext.create('Ext.toolbar.Toolbar',{
                    dock: 'bottom',
                    items: [prevButton, '->', nextButton]
                });
                comp.addDocked(toolbar);
            }
        }, this);

    },

    onStakeholderDetailCenterPanelRender: function(comp) {

        var store = this.getStakeholderDetailWindow().getHistoryStore();

        var toolbar = comp.down('toolbar[dock="bottom"]');
        toolbar ? comp.remove(toolbar) : null;

        store.on('load', function(store, records, successful){

            if(store.first().get('status') == 'pending'){

                var panel = Ext.create('Lmkp.view.moderator.Review',{
                    itemId: 'reviewPanel',
                    store: store,
                    type: 'stakeholders'
                });

                comp.add(panel);

                var prevButton = Ext.create('Ext.button.Button',{
                    disabled: true,
                    itemId: 'card-prev',
                    handler: function(btn) {
                        var layout = comp.getLayout();
                        if(layout.getPrev()){
                            layout.setActiveItem(layout.getPrev());
                        }
                        btn.setDisabled(!layout.getPrev());
                        nextButton.setDisabled(!layout.getNext());
                    },
                    text: '&laquo; Back'
                });

                var nextButton = Ext.create('Ext.button.Button',{
                    itemId: 'card-next',
                    handler: function(btn){
                        var layout = comp.getLayout();
                        if(layout.getNext()){
                            layout.setActiveItem(layout.getNext());
                        }
                        btn.setDisabled(!layout.getNext());
                        prevButton.setDisabled(!layout.getPrev());
                    },
                    text: 'Review pending changes &raquo;'
                });

                toolbar = Ext.create('Ext.toolbar.Toolbar',{
                    dock: 'bottom',
                    items: [prevButton, '->', nextButton]
                });
                comp.addDocked(toolbar);
            }
        }, this);

    },

    onCardPreviousClick: function(button, event){
        var layout = this.getActivityDetailWizardPanel().getLayout();
        layout.setActiveItem(layout.getPrev());
    }
    
});