Ext.define('Lmkp.view.activities.NewActivityWindow', {
    extend: 'Lmkp.view.NewItem',

    requires: [
    'Lmkp.view.stakeholders.StakeholderFieldContainer'
    ],
	
    title: 'Add new Activity',

    config: {
        activityGeometry: {}
    },
	
    layout: 'fit',
    defaults: {
        border: 0
    },
    width: 400,

    initComponent: function() {
		
        // prepare the form
        var form = Ext.create('Ext.form.Panel', {
            border: 0,
            bodyPadding: 5,
            layout: 'anchor',
            defaults: {
                anchor: '100%'
            },
            buttons: [{
                text: 'Cancel',
                handler: function(){
                    this.activityGeometry = null;
                    this.hide();
                },
                scope: this
            },{
                formBind: true,
                disabled: true,
                text: 'Submit',
                handler: function() {
                    var theform = this.up('form').getForm();
                    if (theform.isValid()) {
						
                        // The form cannot be submitted 'normally' because ActivityProtocol expects a JSON object.
                        // As a solution, the form values are used to create a JSON object which is sent using an
                        // AJAX request.
                        // http://www.sencha.com/forum/showthread.php?132082-jsonData-in-submit-action-of-form

                        // collect values and fill them into TagGroups
                        // TODO: it seems that the main tag (first added to dict) always remains in first position, but
                        // maybe this should be ensured in a better way ...
                        var taggroups = [];
                        var stakeholders = [];

                        // Get the geometry
                        var geometry = null;
                        var geojson = new OpenLayers.Format.GeoJSON();
                        var activityGeometry = this.up('window').activityGeometry;
                        if(activityGeometry){
                            geometry = Ext.decode(geojson.write(activityGeometry));
                        }

                        var comps = form.query('lo_stakeholderfieldcontainer');
                        for(var j = 0; j < comps.length; j++ ) {
                            var fieldContainer = comps[j];
                            var stakeholder = {}
                            stakeholder['id'] = fieldContainer.getStakeholderId();
                            stakeholder['role'] = fieldContainer.getStakeholderRole();
                            stakeholder['op'] = 'add';
                            stakeholders.push(stakeholder);
                        }
						
                        for (var i in form.getValues()) {
                            if(i.split('.')[0] != 'stakeholder') {
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
                        }
                        var diffObject = {
                            'activities': [{
                                'taggroups': taggroups,
                                'geometry': geometry,
                                'stakeholders': stakeholders
                            }]
                        };

                        // send JSON through AJAX request
                        Ext.Ajax.request({
                            url: '/activities',
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json;charset=utf-8'
                            },
                            jsonData: diffObject,
                            success: function() {
                                Ext.Msg.alert('Success', 'The activity was successfully created. It will be reviewed shortly.');
                                form.up('window').close();
                            },
                            failure: function() {
                                Ext.Msg.alert('Failure', 'The activity could not be created.');
                            }
                        });
                    }
                }
            }]
        });
		
        // load a store containing only the mandatory fields.
        var mandatoryStore = Ext.create('Lmkp.store.ActivityConfig');
        mandatoryStore.filter("allowBlank", false);
        mandatoryStore.load();
    	
        // load a store containing only the optional fields.
        // This is needed to keep track of all the optional fields available.
        var optionalStore_complete = Ext.create('Lmkp.store.ActivityConfig');
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

        form.add({
            xtype: 'fieldset',
            title: 'Associated Stakeholders',
            //layout: 'fit',
            /*defaults: {
                anchor: '100%'
            },*/
            border: 1,
            items: [
            {
                xtype: 'lo_stakeholderfieldcontainer'
            }]
        });
		
        this.items = form;

        this.callParent(arguments);
    } 
});
