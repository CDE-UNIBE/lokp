Ext.define('Lmkp.controller.activities.TagGroup', {
    extend: 'Ext.app.Controller',

    refs: [{
        ref: 'tagGroupPanel',
        selector: 'lo_taggrouppanel'
    }],

    init: function() {
        this.control({
            'lo_taggrouppanel button[name=toggleDetails]': {
                toggle: this.onTaggroupDetailsToggle
            }
        });
    },

    onTaggroupDetailsToggle: function(button, pressed) {
        var taggrouppanel = button.up('lo_taggrouppanel');
        if (taggrouppanel) {
            taggrouppanel._toggleTags(pressed);
        }
    }

});


