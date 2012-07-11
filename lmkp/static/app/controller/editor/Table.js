Ext.define('Lmkp.controller.editor.Table', {
    extend: 'Ext.app.Controller',

    stores: [
    ],

    views: [
    ],

    init: function() {
        this.control({
            'gridpanel[itemId=resultgrid] gridcolumn[name=nameofinvestorcolumn]': {
                afterrender: this.renderNameofinvestorColumn
            },
            'gridpanel[itemId=resultgrid] gridcolumn[name=yearofinvestmentcolumn]': {
                afterrender: this.renderYearofinvestmentColumn
            },
            'gridpanel[itemId=resultgrid]': {
                selectionchange: this.onSelectionChange
            }
        });
    },

    renderNameofinvestorColumn: function(comp, eOpts) {
        comp.renderer = function(value, p, record) {
            // loop through all tags is needed
            var taggroupStore = record.taggroups();
            var ret = [];
            for (var i=0; i<taggroupStore.count(); i++) {
                var tagStore = taggroupStore.getAt(i).tags();
                for (var j=0; j<tagStore.count(); j++) {
                    if (tagStore.getAt(j).get('key') == Lmkp.ts.msg("activity-nameofinvestor")) {
                        ret.push(Ext.String.format('{0}', tagStore.getAt(j).get('value')));
                    }
                }
            }
            if (ret.length > 0) {
                return ret.join(', ');
            } else {
                return Lmkp.ts.msg("unknown");
            }
        }
    },

    renderYearofinvestmentColumn: function(comp, eOpts) {
        comp.renderer = function(value, p, record) {
            // loop through all tags is needed
            var taggroupStore = record.taggroups();
            for (var i=0; i<taggroupStore.count(); i++) {
                var tagStore = taggroupStore.getAt(i).tags();
                for (var j=0; j<tagStore.count(); j++) {
                    if (tagStore.getAt(j).get('key') == Lmkp.ts.msg("activity-yearofinvestment")) {
                        return Ext.String.format('{0}', tagStore.getAt(j).get('value'));
                    }
                }
            }
            return Lmkp.ts.msg("unknown");
        }
    },

    onSelectionChange: function(model, selected, eOpts) {

        // Unselect all selected features on the map
        //var mapPanel = Ext.ComponentQuery.query('mappanel')[0];
        //var selectControl = mapPanel.getMap().getControlsBy('id', 'selectControl')[0];

        // Get the vector layer from the map panel
        /*var vectorLayer = mapPanel.getVectorLayer();

        // Unregister the featureunselected event and unselect all features
        vectorLayer.events.unregister('featureunselected', this, this.onFeatureUnselected);
        selectControl.unselectAll();
        // Register again the featureunselected event
        vectorLayer.events.register('featureunselected', this, this.onFeatureUnselected);

        // If there are selected records, highlight it on the map
        if(selectedRecord[0]){
            // Get the acitvity identifier
            var id = selectedRecord[0].data.id;

            // Get the feature by its fid
            var feature = vectorLayer.getFeatureByFid(id);

            // Unregister and register again the featureselected event
            vectorLayer.events.unregister('featureselected', this, this.onFeatureSelected);
            // Select the feature
            selectControl.select(feature);
            vectorLayer.events.register('featureselected', this, this.onFeatureSelected);
        }*/

        var detailPanel = Ext.ComponentQuery.query('lo_editortablepanel lo_editordetailpanel')[0];
        var activeTab = detailPanel.getActiveTab();
        switch (activeTab.getXType()) {
            case "activityHistoryTab":
                // var uid = (selectedRecord.length > 0) ? selectedRecord[0].raw['activity_identifier'] : null;
                // detailPanel._populateHistoryTab(selectedTab, uid)
                console.log("coming soon");
                break;
            default: 	// default is: activityDetailTab
                detailPanel.populateDetailsTab(activeTab, selected);
                break;
        }
    }

});