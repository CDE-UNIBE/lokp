Ext.define('Lmkp.controller.Stakeholder', {
    extend: 'Ext.app.Controller',

    stores: [
    'StakeholderGrid'
    ],

    views: [
    'Stakeholder',
    'stakeholders.Detail'
    ],

    init: function(){
        this.control({
            'stakeholderpanel': {
                render: this.onPanelRender
            },
            'stakeholderpanel gridcolumn[itemId=stakeholder-name-column]': {
                afterrender: this.onNameColumnAfterRender
            },
            'stakeholderpanel gridcolumn[itemId=stakeholder-country-column]': {
                afterrender: this.onCountryColumnAfterRender
            },
            'stakeholderpanel gridview': {
                itemclick: this.onGridViewItemClick
            }
        });
    },

    onPanelRender: function(comp, eOpts){
        var gridpanel = comp.query('gridpanel')[0];
        var store = gridpanel.getStore();
        store.load();
    },

    onNameColumnAfterRender: function(comp, eOpts){
        comp.renderer = function(value, p, record) {
            // loop through all tags is needed
            var taggroupStore = record.taggroups();
            for (var i=0; i<taggroupStore.count(); i++) {
                var tagStore = taggroupStore.getAt(i).tags();
                for (var j=0; j<tagStore.count(); j++) {
                    if (tagStore.getAt(j).get('key') == Lmkp.ts.msg("stakeholder-name")) {
                        return Ext.String.format('{0}', tagStore.getAt(j).get('value'));
                    }
                }
            }
            return Lmkp.ts.msg("unknown");
        }
    },

    onCountryColumnAfterRender: function(comp, eOpts){
        comp.renderer = function(value, p, record) {
            // loop through all tags is needed
            var taggroupStore = record.taggroups();
            for (var i=0; i<taggroupStore.count(); i++) {
                var tagStore = taggroupStore.getAt(i).tags();
                for (var j=0; j<tagStore.count(); j++) {
                    if (tagStore.getAt(j).get('key') == Lmkp.ts.msg("stakeholder-country")) {
                        return Ext.String.format('{0}', tagStore.getAt(j).get('value'));
                    }
                }
            }
            return Lmkp.ts.msg("unknown");
        }
    },

    onGridViewItemClick: function(view, record, item, index, event, eOpts){
        console.log("clickckckckckckc");
    }

});