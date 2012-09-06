Ext.define('Lmkp.controller.stakeholders.NewStakeholder', {
    extend: 'Ext.app.Controller',

    views: [
    'stakeholders.NewStakeholder'
    ],

    init: function(){
        this.control({
            'lo_newstakeholderpanel button[itemId="cancelButton"]': {
                click: this.onCancelButtonClick
            },
            'lo_newstakeholderpanel button[itemId="submitButton"]': {
                click: this.onSubmitButtonClick
            }
        });
    },

    onCancelButtonClick: function(button, event, eOpts){
        button.up('window').destroy();
    },

    onSubmitButtonClick: function(button, event, eOpts){
        var me = this;
        var form = button.up('form');
        var p = button.up('lo_newstakeholderpanel');
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
                callback: function(options, success, response) {
                    if(success) {
                        Ext.Msg.alert('Success', 'The stakeholder was successfully created. It will be reviewed shortly.');

                        // Put newly created Stakeholder into a store.
                        var store = Ext.create('Ext.data.Store', {
                            autoLoad: true,
                            model: 'Lmkp.model.Stakeholder',
                            data : Ext.decode(response.responseText),
                            proxy: {
                                type: 'memory',
                                reader: {
                                    root: 'data',
                                    type: 'json',
                                    totalProperty: 'total'
                                }
                            }
                        });

                        // Add newly created Stakeholder to fieldset in other
                        // window
                        var newActivityController =
                            me.getController('activities.NewActivity');
                        newActivityController._onNewStakeholderCreated(
                            store.getAt(0)
                        );

                    } else {
                        Ext.Msg.alert('Failure', 'The stakeholder could not be created.');
                        this.setAddedStakeholder(null);
                    }
                    this.up('window').close();
                },
                scope: p
            });
        }
    }
});