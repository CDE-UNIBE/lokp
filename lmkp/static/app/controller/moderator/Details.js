Ext.define('Lmkp.controller.moderator.Details', {
    extend: 'Ext.app.Controller',

    models: [
    ],

    refs: [{
        ref: 'activityDetailWindow',
        selector: 'lo_activitydetailwindow'
    }],

    requires: [
    ],

    stores: [
    'ActivityConfig',
    'ActivityGrid'
    ],

    views: [
    'activities.Details',
    'activities.Filter',
    'moderator.Review'
    ],

    init: function() {
        this.control({
            'lo_activitydetailwindow panel[itemId="activityDetailCenterPanel"]':{
                render: this.onActivityDetailCenterPanelRender
            }
        });
    },

    onActivityDetailCenterPanelRender: function(comp){

        var toolbar = comp.down('toolbar[dock="bottom"]');
        toolbar ? comp.remove(toolbar) : null;

        if(comp.currentActivity.get('status') == 'pending'){

            var wrapperPanel = comp.up('panel');

            /* var reviewPanel = Ext.create('Ext.form.Panel',{
                bbar: {
                    items: [{
                        itemId: 'card-prev',
                        handler: function(btn) {
                            var layout = wrapperPanel.getLayout();
                            if(layout.getPrev()){
                                layout.setActiveItem(layout.getPrev());
                            }
                        },
                        text: '&laquo; Back'
                    }]
                },
                bodyPadding: 5,
                buttons: [{
                    handler: function(btn){
                        btn.up('form').submit({
                            failure: function(form, action) {
                                Ext.Msg.alert("error", "some kind of error");
                            },
                            method: 'GET',
                            params: {
                                limit: 1
                            },
                            success: function(form, action){
                                Ext.Msg.alert("great", "Great");
                            },
                            url: '/activities'
                        });
                    },
                    iconCls: 'save-button',
                    text: 'Submit Review',
                    scale: 'medium'
                }],
                defaults: {
                    anchor: "100%"
                },
                items: [{
                    fieldLabel: 'Review decision',
                    store: [['approved', 'Approved'], ['rejected', 'Rejected'], ['edited', 'Edited']],
                    value: 'approved',
                    xtype: 'combo'
                },{
                    cols: 10,
                    fieldLabel: 'Review comment',
                    xtype: 'textarea'
                }],
                margin: 3
            });

            wrapperPanel.add(reviewPanel);*/

            var store = this.getActivityDetailWindow().getHistoryStore();
            store.on('load', function(store, records){
                var panel = Ext.create('Lmkp.view.moderator.Review',{
                    itemId: 'reviewPanel',
                    store: store,
                    type: 'activities'
                });
                wrapperPanel.add(panel);
            }, this);
            
            var prevButton = Ext.create('Ext.button.Button',{
                disabled: true,
                itemId: 'card-prev',
                handler: function(btn) {
                    var layout = wrapperPanel.getLayout();
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
                    var layout = wrapperPanel.getLayout();
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
            wrapperPanel.addDocked(toolbar);
        }

    },

    onCardPreviousClick: function(button, event){
        var panel = button.up('detailWizardPanel');
        var layout = panel.getLayout();
        layout.setActiveItem(layout.getPrev());
    }
    
});