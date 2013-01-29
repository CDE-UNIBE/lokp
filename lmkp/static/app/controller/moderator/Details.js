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
        if (toolbar) {
            comp.remove(toolbar);
        }

        store.on('load', function(store, records, successful) {
            if (store.find('status', Lmkp.ts.msg('status_pending')) > -1) {
                toolbar = Ext.create('Ext.toolbar.Toolbar',{
                    dock: 'bottom',
                    items: [
                        '->', {
                            text: Lmkp.ts.msg('moderator_review-pending-changes'),
                            tooltip: 'This item has pending changes. Click to review them in a popup window.',
                            handler: function() {
                                var record = store.first();
                                if (record) {
                                    var url = '/moderation/activities/' + record.get('id');
                                    window.open(url, 'lo_compareview');
                                }
                            }
                        }
                    ]
                });
                comp.addDocked(toolbar);
            }
        }, this);
    },

    onStakeholderDetailCenterPanelRender: function(comp) {

        var store = this.getStakeholderDetailWindow().getHistoryStore();

        var toolbar = comp.down('toolbar[dock="bottom"]');
        if (toolbar) {
            comp.remove(toolbar);
        }

        store.on('load', function(store, records, successful) {
            if (store.find('status', Lmkp.ts.msg('status_pending')) > -1) {
                toolbar = Ext.create('Ext.toolbar.Toolbar',{
                    dock: 'bottom',
                    items: [
                        '->', {
                            text: Lmkp.ts.msg('moderator_review-pending-changes'),
                            tooltip: 'This item has pending changes. Click to review them in a popup window.',
                            handler: function() {
                                var record = store.first();
                                if (record) {
                                    var url = '/moderation/stakeholders/' + record.get('id');
                                    window.open(url, 'lo_compareview');
                                }
                            }
                        }
                    ]
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