Ext.define('Lmkp.view.editor.Detail', {
    extend: 'Ext.tab.Panel',
    alias: ['widget.lo_editordetailpanel'],

    requires: [
        'Lmkp.view.comments.CommentPanel',
        'Lmkp.view.activities.ActivityPanel',
        'Lmkp.view.items.PendingUserChanges'
    ],

    config: {
        // The currently shown activity in this panel or null if no activity
        // is shown
        current: {},
        // The OpenLayers GeoJSON format
        geojson: {}
    },

    geojson: new OpenLayers.Format.GeoJSON(),
	
    plain: true,
    activeTab: 0,
    defaults: {
        autoScroll: true
    },

    items: [{
        title: 'Details',
        xtype: 'lo_activitydetailtab'
    }, {
        title: 'History',
        xtype: 'lo_activityhistorypanel'
    }, {
        title: 'Add new Activity',
        xtype: 'lo_newactivitypanel'
    }],

    initComponent: function() {
        this.callParent(arguments);
    },

    populateDetailsTab: function(panel, data) {

        if (data) {

            // Activity or Stakeholder?
            var xtype = null;
            if (data.modelName == 'Lmkp.model.Activity') {
                xtype = 'lo_activitypanel';
            } else if (data.modelName == 'Lmkp.model.Stakeholder') {
                xtype = 'lo_stakeholderpanel';
            }

            // Set the current selection to current
            this.current = data;

            // Remove all existing panels
            panel.removeAll();

            if (data.raw.pending) {
                // If the user has current versions pending

                // Show a notice
                panel.add({
                    bodyPadding: 5,
                    html: 'You are seeing a pending version, which needs to be \n\
                        reviewed before it is publicly visible',
                    bodyCls: 'notice'
                });
                // Display latest pending version
                panel.add({
                    xtype: xtype,
                    contentItem: data.raw.pending[0],
                    border: 0,
                    bodyPadding: 0,
                    editable: true
                });
                // Show original active version (hidden)
                panel.add({
                    xtype: xtype,
                    contentItem: data,
                    editable: true,
                    hiddenOriginal: true,
                    bodyCls: 'notice'
                });
                // Show other pending changes
                if (data.raw.pending.length > 1) {
                    // Remove the first pending version (shown already)
                    data.raw.pending.shift();
                    panel.add({
                        xtype: 'lo_itemspendinguserchanges',
                        detailData: data.raw.pending,
                        itemModel: data.modelName,
                        detailsOnStart: false,
                        bodyCls: 'notice'
                    });
                }

            } else {
                // If there are no versions pending, simply show active version
                panel.add({
                    xtype: xtype,
                    contentItem: data,
                    border: 0,
                    bodyPadding: 0,
                    editable: true
                });
            }

            // Add commenting panel
            panel.add({
                xtype: 'lo_commentpanel',
                identifier: data.get('id'),
                comment_object: 'activity'
            });

            // Show the feature on the map
            // Actually this does not belong here ...
            var mappanel = Ext.ComponentQuery.query('lo_editormappanel')[0];
            var vectorLayer = mappanel.getVectorLayer();
            vectorLayer.removeAllFeatures();
            var features = this.getFeatures(data);
            if (features) {
                vectorLayer.addFeatures(features);
            }
            vectorLayer.events.remove('featureunselected');
            vectorLayer.events.register('featureunselected',
                this,
                function(event){
                    Ext.MessageBox.confirm("Save changes?",
                        "Do you want to save the changes?",
                        function(buttonid){
                            // In case of yes, save the feature
                            if(buttonid == 'yes'){
                                // do something
                                this.saveGeometry(data, event.feature.geometry);
                            }
                            // If no is selected, reset the features
                            else if(buttonid == 'no'){
                                vectorLayer.removeAllFeatures();
                                vectorLayer.addFeatures(this.getFeatures(data));
                            }
                        }, this);
                });
        }
    },

    getFeatures: function(data){
        var geom = data.get('geometry');
        var vectors = this.geojson.read(Ext.encode(geom));
        if (vectors) {
            for(var j = 0; j < vectors.length; j++){
                vectors[j].geometry.transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913"));
            }
            return vectors

        }
    },

    /**
     * Add a new geometry to an existing activity.
     */
    saveGeometry: function(data, newGeometry){
        // Create the geojson object
        var geom = Ext.decode(
            this.geojson.write(
                // Project the point back to geographic coordinates
                newGeometry.transform(new OpenLayers.Projection("EPSG:900913"),
                    new OpenLayers.Projection("EPSG:4326"))
                )
            );

        // Create the diff object
        var activities = [];
        var activity = new Object();
        activity.id = data.get('id');
        activity.geometry = geom;
        activity.taggroups = [];
        activity.version = data.get('version');

        activities.push(activity);

        // Send JSON through AJAX request
        Ext.Ajax.request({
            url: '/activities',
            method: 'POST',
            headers: {
                'Content-Type': 'application/json;charset=utf-8'
            },
            jsonData: {
                'activities': activities
            },
            success: function() {
                Ext.Msg.alert('Success', 'The activity was successfully updated. It will be reviewed shortly.');
            },
            failure: function() {
                Ext.Msg.alert('Failure', 'The activity could not be created.');
            }
        });
    }
});
