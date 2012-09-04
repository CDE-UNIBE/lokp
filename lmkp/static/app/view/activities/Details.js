Ext.define('Lmkp.view.activities.Details', {
    extend: 'Ext.window.Window',
    alias: ['widget.lo_activitydetailwindow'],

    bodyPadding: 5,
    modal: true,
    
    config: {
        centerPanel: null,
        historyPanel: null,
        historyStore: null
    },
    
    defaults: {
        margin: '0 0 5 0',
        anchor: '100%'
    },
    
    itemId: 'activityDetailWindow',

    layout: 'border',
    height: 400,
    width: 600,

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

    initComponent: function(){

        this.centerPanel = Ext.create('Ext.panel.Panel',{
            region: 'center',
            layout: 'anchor',
            autoScroll: true,
            title: 'Details'
        });
        

        this.historyStore = Ext.create('Ext.data.Store', {
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
            proxy: {
                reader: {
                    root: 'data',
                    type: 'json',
                    totalProperty: 'total'
                },
                simpleSortMode: true,
                sortParam: 'order_by',
                startParam: 'offset',
                type: 'ajax',
                url: '/activities/history/' + this.activity.get('id')
            },
            remoteSort: true
        });

        this.historyPanel = Ext.create('Ext.grid.Panel',{
//            collapsed: true, 
            collapsible: true,
            collapseMode: 'header',
            columns: [{
                dataIndex: 'version',
                flex: 1,
                text: 'Version'
            }, {
                dataIndex: 'status',
                flex: 1,
                text: 'Status'
            }, {
            	dataIndex: 'timestamp',
            	flex: 1,
            	text: 'Timestamp'
            }],
            itemId: 'historyPanel',
            region: 'west',
            store: this.historyStore,
            title: 'History',
            width: 250
        });

        this._populateDetails(this.activity)

        this.items = [
        this.centerPanel,
        this.historyPanel
        ];

        this.title = 'Details on Activity ' + this.activity.get('id');

        this.callParent(arguments);
    },

    /**
<<<<<<< HEAD
 * Parameter activity is an instance of Lmkp.model.Activity
 */
=======
     * Ext has some serious issues with panels collapsed on start. Instead, this
     * function is called right after showing this window.
     */
    _collapseHistoryPanel: function() {
        if (this.historyPanel) {
            this.historyPanel.collapse();
        }
    },

    /**
     * Parameter activity is an instance of Lmkp.model.Activity
     */
>>>>>>> b33bd569272e76068610f61b46170f8031a005f6
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
                editable: true,
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
