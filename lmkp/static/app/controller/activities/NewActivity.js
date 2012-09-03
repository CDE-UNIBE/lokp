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
            'lo_newactivitypanel button[itemId="selectStakeholderButton"]': {
                click: this.onStakeholderButtonClick
            },
            'lo_newactivitypanel button[name=addAdditionalTagButton]': {
                click: this.onAddAdditionalTagButtonClick
            },
            'lo_newactivitypanel button[itemId=addAdditionalTaggroupButton]': {
                click: this.onAddAdditionalTaggroupButtonClick
            },
            'lo_newactivitypanel button[itemId=submitButton]': {
            	click: this.onSubmitButtonClick
            },
            // Intercept normal functionality of button (defined in
            // Lmkp.view.activities.NewTaggroupPanel)
            'lo_newactivitypanel lo_newtaggrouppanel button[name=deleteTag]': {
                click: this.onDeleteTagButtonClick
            }
        });
    },

    /**
     * If the last item of a form is to be removed, destroy entire form panel.
     */
    onDeleteTagButtonClick: function(button) {
        var form = button.up('form');
        if (form && form.items.length == 1) {
            // Disable form first in order to keep track of fields that are not
            // allowed blank
            form.disable();
            form.destroy();
        }
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

    onAddAdditionalTagButtonClick: function(button) {
        var form = button.up('form');
        var newtaggrouppanel = form.down('lo_newtaggrouppanel')
        if (form && newtaggrouppanel) {
            form.add({
                xtype: 'lo_newtaggrouppanel',
                is_maintag: false,
                removable: true,
                main_store: newtaggrouppanel.main_store,
                complete_store: newtaggrouppanel.complete_store
            });
        }
    },

    onAddAdditionalTaggroupButtonClick: function(button) {
        var form = button.up('form');
        var panel = form.up('panel');

        if (form && panel) {
            // create the stores
            var mainStore = Ext.create('Lmkp.store.ActivityConfig');
            mainStore.load(function() {
                // Create and load a second store with all keys
                var completeStore = Ext.create('Lmkp.store.ActivityConfig');
                completeStore.load(function() {
                    // When loaded, show panel
                    form.insert(form.items.length - 2, panel._getFieldset(
                        mainStore,
                        completeStore,
                        null
                    ));
                });
            });
        }
    },
    
    onSubmitButtonClick: function(button) {
    	var me = this;
        var formpanel = button.up('form');
        var theform = formpanel.getForm();
        if (theform.isValid()) {
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

            // Loop through each form panel (they form taggroups)
            var forms = formpanel.query('form[name=taggroupfieldset]');
            for (var i in forms) {
                var tags = [];
                var main_tag = new Object();
                // Within a taggroup, loop through each tag
                var tgpanels = forms[i].query('lo_newtaggrouppanel');
                for (var j in tgpanels) {
                    var c = tgpanels[j];
                    tags.push({
                        'key': c.getKeyValue(),
                        'value': c.getValueValue(),
                        'op': 'add'
                    });
                    if (c.isMainTag()) {
                        main_tag.key = c.getKeyValue();
                        main_tag.value = c.getValueValue()
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
                'activities': [{
                    'taggroups': taggroups,
                    'geometry': geometry,
                    'stakeholders': stakeholders
                }]
            };
            
            console.log(diffObject);
            
            // TODO: how and when to add geometry? What was there about 
            // card / wizard layout?

            // send JSON through AJAX request
            // Ext.Ajax.request({
                // url: '/activities',
                // method: 'POST',
                // headers: {
                    // 'Content-Type': 'application/json;charset=utf-8'
                // },
                // jsonData: diffObject,
                // callback: function(options, success, response) {
                    // if(success){
                        // Ext.Msg.alert('Success', 'The activity was successfully created. It will be reviewed shortly.');
// 
                        // var p = this.getNewActivityPanel();
                        // p.setActivityGeometry(null);
// 
                        // // Reset form
                        // var controller = me.getController('editor.Detail');
                        // controller.onNewActivityTabActivate(p);
// 
                        // var fieldContainers = formpanel.query('lo_stakeholderfieldcontainer');
                        // for(var i = 0; i < fieldContainers.length; i++){
                            // this.getSelectStakeholderFieldSet().remove(fieldContainers[i]);
                        // }
// 
                        // // Remove also the feature on the map
                        // this.getMapPanel().getVectorLayer().removeAllFeatures();
                    // } else {
                        // Ext.Msg.alert('Failure', 'The activity could not be created.');
                    // }
// 
                // },
                // scope: this
            // });
    	}
    	
    }

});