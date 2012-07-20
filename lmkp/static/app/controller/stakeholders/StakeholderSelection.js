Ext.define('Lmkp.controller.stakeholders.StakeholderSelection', {
    extend: 'Ext.app.Controller',

    views: [
    'stakeholders.StakeholderSelection'
    ],

    init: function(){
        this.control({
            'lo_stakeholderselection gridcolumn[itemId=stakeholderNameColumn]': {
                render: this.onNameColumnRender
            }
        });
    },

    onNameColumnRender: function(comp, eOpts){
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
    }

});