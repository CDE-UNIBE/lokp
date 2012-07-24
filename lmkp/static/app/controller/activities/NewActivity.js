Ext.define('Lmkp.controller.activities.NewActivity', {
    extend: 'Ext.app.Controller',

    refs: [{
        ref: 'newActivityPanel',
        selector: 'lo_newactivitypanel'
    },{
        ref: 'selectStakeholderFieldSet',
        selector: 'lo_newactivitypanel fieldset[itemId="selectStakeholderFieldSet"]'
    }],

    views: [
    'activities.NewActivity'
    ],

    init: function(){
        this.control({
            'lo_newactivitypanel button[itemId="submitButton"]': {
                click: this.onSubmitButtonClick
            },
            'lo_newactivitypanel button[itemId="selectStakeholderButton"]': {
                click: this.onStakeholderButtonClick
            }
        });
    },

    onStakeholderButtonClick: function(button, event){
        var sel = Ext.create('Lmkp.view.stakeholders.StakeholderSelection');

        var w = this.getNewActivityPanel();

        sel.on('close', function(panel, eOpts){
            var sh = panel.getSelectedStakeholder();
            this.getSelectStakeholderFieldSet().insert(
                0, {
                    stakeholder: sh,
                    xtype: 'lo_stakeholderfieldcontainer'
                });
        }, this);
        sel.show();
    },

    onSubmitButtonClick: function(button, event){
        var formpanel = button.up('form');
        var theform = formpanel.getForm();
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
            if(this.getNewActivityPanel().getActivityGeometry()){
                geometry = Ext.decode(geojson.write(this.getNewActivityPanel().getActivityGeometry()));
            }

            var comps = formpanel.query('lo_stakeholderfieldcontainer');
            for(var j = 0; j < comps.length; j++ ) {
                var fieldContainer = comps[j];
                var stakeholder = {}
                stakeholder['id'] = fieldContainer.getStakeholderId();
                //stakeholder['role'] = fieldContainer.getStakeholderRole();
                stakeholder['role'] = 6;
                stakeholder['version'] = fieldContainer.getStakeholderVersion();
                stakeholder['op'] = 'add';
                stakeholders.push(stakeholder);
            }

            for (var i in formpanel.getValues()) {
                if(i.split('.')[0] != 'stakeholder') {
                    var tags = [];
                    var main_tag = {};
                    // first, look only at mandatory fields (no '__val' or '__attr' in name)
                    if (i.indexOf("__attr") == -1 && i.indexOf("__val") == -1) {
                        var tag = {};
                        tag['key'] = i;
                        tag['value'] = formpanel.getValues()[i];
                        tag['op'] = 'add';
                        tags.push(tag);
                        // also add to main_tag
                        main_tag['key'] = i;
                        main_tag['value'] = formpanel.getValues()[i];

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
                callback: function(options, success, response) {
                    if(success){
                        Ext.Msg.alert('Success', 'The activity was successfully created. It will be reviewed shortly.');

                        var p = this.getNewActivityPanel();
                        p.setActivityGeometry(null);
                        var formpanel = p.down('form');
                        formpanel.getForm().reset();
                        
                        var fieldContainers = formpanel.query('lo_stakeholderfieldcontainer');
                        for(var i = 0; i < fieldContainers.length; i++){
                            this.getSelectStakeholderFieldSet().remove(fieldContainers[i]);
                        }
                    } else {
                        Ext.Msg.alert('Failure', 'The activity could not be created.');
                    }
                    
                },
                scope: this
            });
        }
    }

});