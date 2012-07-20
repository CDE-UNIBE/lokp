Ext.define('Lmkp.view.stakeholders.NewStakeholder', {
    extend: 'Lmkp.view.NewItem',

    title: 'Add new Stakeholder',

    layout: 'fit',
    defaults: {
        border: 0
    },

    items: [{
        buttons:[{
            handler: function(button, event){
                button.up('window').hide();
            },
            text: 'Cancel'
        },{
            formBind: true,
            disabled: true,
            handler: function(button, event) {
                var form = this.up('form');
                if (form.getForm().isValid()) {

                    // The form cannot be submitted 'normally' because ActivityProtocol expects a JSON object.
                    // As a solution, the form values are used to create a JSON object which is sent using an
                    // AJAX request.
                    // http://www.sencha.com/forum/showthread.php?132082-jsonData-in-submit-action-of-form

                    // collect values and fill them into TagGroups
                    // TODO: it seems that the main tag (first added to dict) always remains in first position, but
                    // maybe this should be ensured in a better way ...
                    var taggroups = [];

                    for (var i in form.getValues()) {
                        var tags = [];
                        var main_tag = {};
                        // first, look only at mandatory fields (no '__val' or '__attr' in name)
                        if (i.indexOf("__attr") == -1 && i.indexOf("__val") == -1) {
                            var tag = {};
                            tag['key'] = i;
                            tag['value'] = form.getValues()[i];
                            tag['op'] = 'add';
                            tags.push(tag);
                            // also add to main_tag
                            main_tag['key'] = i;
                            main_tag['value'] = form.getValues()[i];

                            // look if further attributes to this field were entered
                            var attrs = Ext.ComponentQuery.query('[name=' + i + '__attr]');
                            var vals = Ext.ComponentQuery.query('[name=' + i + '__val]');
                            if (attrs.length > 0 && vals.length > 0 && attrs.length == vals.length) {
                                for (var j=0; j<attrs.length; j++) {
                                    var tag = {};
                                    tag['key'] = attrs[j].getValue();
                                    tag['value'] = vals[j].getValue();
                                    tag['op'] = 'add';
                                    tags.push(tag);
                                }
                            }
                        }
                        if (tags.length > 0) {
                            taggroups.push({
                                'tags': tags,
                                'main_tag': main_tag
                            });
                        }
                    }
                    var diffObject = {
                        'stakeholders': [{
                            'taggroups': taggroups
                        }]
                    };

                    // send JSON through AJAX request
                    Ext.Ajax.request({
                        url: '/stakeholders',
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json;charset=utf-8'
                        },
                        jsonData: diffObject,
                        success: function() {
                            Ext.Msg.alert('Success', 'The stakeholder was successfully created. It will be reviewed shortly.');
                            form.up('window').close();
                        },
                        failure: function() {
                            Ext.Msg.alert('Failure', 'The stakeholder could not be created.');
                        }
                    });
                }
            },
            text: 'Submit'
        }],
        xtype: 'form'
    }],

    width: 400,

    initComponent: function(){

        this.callParent(arguments);

        var form = this.down('form');

        // load a store containing only the mandatory fields.
        var mandatoryStore = Ext.create('Lmkp.store.StakeholderConfig');
        mandatoryStore.filter("allowBlank", false);
        mandatoryStore.load();

        // load a store containing only the optional fields.
        // This is needed to keep track of all the optional fields available.
        var optionalStore_complete = Ext.create('Lmkp.store.StakeholderConfig');
        // for some reason, 'normal' filtering of stores does not work (asynchronous problem?)
        // instead, 'filtering' is done manually
        optionalStore_complete.on('load', function(store) {
            store.each(function(record) {
                if (record.get('allowBlank') != true) {
                    store.remove(record);
                }
            });
        });
        optionalStore_complete.load();

        // create a field for each mandatory attribute.
        mandatoryStore.on('load', function(store) {
            store.each(function(record) {
                form.up('window')._getFormField(form, record, optionalStore_complete);
            });
        });
       
    }

});