Ext.define('Lmkp.controller.Stakeholder', {
    extend: 'Ext.app.Controller',

    stores: [
    'StakeholderGrid'
    ],

    views: [
    'Stakeholder'
    ],

    init: function(){
        this.control({
            'stakeholderpanel': {
                render: this.onPanelRender
            },
            'stakeholderpanel gridcolumn[itemId=stakeholder-name-column]': {
                afterrender: this.onNameColumnAfterRender
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
                    if (tagStore.getAt(j).get('key') == Lmkp.ts.msg("Name")) {
                        return Ext.String.format('{0}', tagStore.getAt(j).get('value'));
                    }
                }
            }
            return Lmkp.ts.msg("unknown");
        }
    }

});