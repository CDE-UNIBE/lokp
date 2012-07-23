Ext.define('Lmkp.model.Stakeholder', {
    extend: 'Ext.data.Model',

    fields: [{
        name: 'id', // activity_identifier (UID)
        type: 'string'
    }, {
        name: 'version',
        type: 'int'
    }],

    hasMany: [{
        model: 'Lmkp.model.TagGroup',
        name: 'taggroups'
    }, {
        model: 'Lmkp.model.Involvement',
        name: 'involvements'
    }],

    getTagValues: function(tag) {

        var values = [];

        var taggroupStore = this.taggroups();
        for (var i = 0; i < taggroupStore.count(); i++) {
            var tagStore = taggroupStore.getAt(i).tags();
            for (var j=0; j < tagStore.count(); j++) {
                if (tagStore.getAt(j).get('key') == tag) {
                    values.push(tagStore.getAt(j).get('value'));
                }
            }
        }
        return values;
    }
});