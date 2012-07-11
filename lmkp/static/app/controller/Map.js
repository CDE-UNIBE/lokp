Ext.define('Lmkp.controller.Map',{
    extend: 'Ext.app.Controller',

    stores: [
        'Profiles'
    ],

    views: [
        'editor.Map'
    ],

    init: function(){

        this.control({
            'mappanel': {
                render: this.onPanelRendered
            }
        });
    },
   

    /*
     * Method on map move end.
     */
    onMoveEnd: function(event){
        // Move paging to back to page 1 when filtering (otherwise may show empty page instead of results)
        Ext.ComponentQuery.query('pagingtoolbar[id=activityGridPagingToolbar]')[0].moveFirst();
    },

    /**
     * Method triggered by the onfeatureunselected event by an OpenLayers.Layer.Vector
     */
    onFeatureUnselected: function(event){
        var grid = Ext.ComponentQuery.query('filterPanel gridpanel[id=filterResults]')[0];
        grid.getSelectionModel().deselectAll(true);
    },

    /**
     * Method triggered by the onfeatureselected event by an OpenLayers.Layer.Vector
     */
    onFeatureSelected: function(event){
        // Get the GridPanel
        var grid = Ext.ComponentQuery.query('filterPanel gridpanel[id=filterResults]')[0];
        //grid.getSelectionModel().deselectAll(true);
        var store = grid.getStore();

        // Get the record from the store with the same id as the selected vector
        var index = store.findBy(function(record, id){
            return event.feature.data.id == id;
        });
        var record = store.getAt(index);
        grid.getSelectionModel().select([record], false, true);

        var detailPanel = Ext.ComponentQuery.query('filterPanel detailPanel')[0];
        var selectedTab = detailPanel.getActiveTab();
        switch (selectedTab.getXType()) {
            case "activityHistoryTab":
                // var uid = (selectedRecord.length > 0) ? selectedRecord[0].raw['activity_identifier'] : null;
                // this._populateHistoryTab(selectedTab, uid)
                console.log("coming soon");
                break;
            default:
                // default is: activityDetailTab
                detailPanel.populateDetailsTab(selectedTab, [record]);
                break;
        }
    }

    
})