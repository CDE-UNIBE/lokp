Ext.define('Lmkp.view.activities.Details', {
    extend: 'Ext.window.Window',
    alias: ['widget.lo_activitydetailwindow'],

    autoScroll: true,

    bodyPadding: 5,
    
    config: {
        centerPanel: null,
        historyPanel: null
    },
    
    itemId: 'activityDetailWindow',

    height: 200,

    layout: 'border',

    requires: [
    'Lmkp.view.activities.ActivityPanel',
    'Lmkp.view.comments.CommentPanel'
    ],

    bbar: {
        items: ['->', {
            iconCls: 'cancel-button',
            text: 'Close', // also translate tooltip
            scale: 'medium',
            itemId: 'closeWindowButton'
        }],
        xtype: 'toolbar'
    },

    width: 800,

    initComponent: function(){

        this.centerPanel = Ext.create('Ext.panel.Panel',{
            region: 'center',
            layout: 'anchor',
            title: 'Details'
        });

        var historyStore = Ext.create('Ext.data.Store', {
            autoLoad: true,
            autoScroll: true,
            storeId: 'historyStore',
            // all are needed to build relation
            requires: [
            'Lmkp.model.Activity',
            'Lmkp.model.TagGroup',
            'Lmkp.model.Tag',
            'Lmkp.model.MainTag',
            'Lmkp.model.Involvement',
            'Lmkp.model.Point'
            ],

            model: 'Lmkp.model.Activity',

            pageSize: 10,
            remoteSort: true,

            proxy: {
                type: 'ajax',
                url: '/activities/history/' + this.activity.get('id'),
                reader: {
                    root: 'data',
                    type: 'json',
                    totalProperty: 'total'
                },
                startParam: 'offset',
                simpleSortMode: true,
                sortParam: 'order_by'
            }
        });

        this.historyPanel = Ext.create('Ext.grid.Panel',{
            collapsed: true,
            collapsible: true,
            collapseMode: 'header',
            columns: [{
                dataIndex: 'version',
                flex: 1,
                text: 'Version'
            },{
                dataIndex: 'status',
                flex: 1,
                text: 'Status'
            }],
            itemId: 'historyPanel',
            region: 'west',
            store: historyStore,
            title: 'History',
            width: 250
        });

        this._populateDetails(this.activity)

        this.items = [
            this.centerPanel,
            this.historyPanel
        ];

        this.title = 'Details Activity ' + this.activity.get('id');

        this.callParent(arguments);
    },

    /**
     * Parameter activity is an instance of Lmkp.model.Activity
     */
    _populateDetails: function(activity){

        if (activity) {

            // Set the current selection to current
            this.current = activity;

            // Remove all existing panels
            this.centerPanel.removeAll();

            // If there are no versions pending, simply show active version
            this.centerPanel.add({
                contentItem: activity,
                border: 0,
                bodyPadding: 0,
                editable: false,
                hiddenOriginal: false,
                xtype: 'lo_activitypanel'
            });

            // Add commenting panel
            this.centerPanel.add({
                xtype: 'lo_commentpanel',
                identifier: activity.get('id'),
                comment_object: 'activity'
            });
            
        }

        this.doLayout();

        return activity;

    }
	
});
