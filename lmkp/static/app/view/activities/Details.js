Ext.define('Lmkp.view.activities.Details', {
    extend: 'Ext.window.Window',
    alias: ['widget.lo_activitydetailwindow'],

    bodyPadding: 5,
    
    config: {
        centerPanel: null,
        historyPanel: null,
        historyStore: null
    },
    
    defaults: {
        anchor: '100%'
    },
    
    itemId: 'activityDetailWindow',

    layout: 'border',

    modal: true,
    height: 500,
    width: 700,

    requires: [
    'Lmkp.view.activities.ActivityPanel',
    'Lmkp.view.comments.CommentPanel'
    ],

    bbar: {
        items: ['->', {
            iconCls: 'cancel-button',
            itemId: 'closeWindowButton',
            scale: 'medium',
            text: 'Close', // also translate tooltip
            tooltip: Lmkp.ts.msg('Close window')
        }],
        xtype: 'toolbar'
    },

    initComponent: function(){

        var activity_identifier;

        this.activity ? activity_identifier = this.activity.get('id') : activity_identifier = this.activity_identifier

        this.centerPanel = Ext.create('Ext.panel.Panel',{
            autoScroll: true,
            layout: 'anchor',
            itemId: 'activityDetailCenterPanel'
        });

        this.historyStore = Ext.create('Ext.data.Store', {
            autoLoad: true,
            autoScroll: true,
            listeners: {
                load: function(store, records, successful){
                    var firstRecord = store.first();
                    this._populateDetails(firstRecord, firstRecord.get('status') == 'pending');
                },
                scope: this
            },
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
                extraParams: {
                    involvements: 'full'
                },
                reader: {
                    root: 'data',
                    type: 'json',
                    totalProperty: 'total'
                },
                simpleSortMode: true,
                sortParam: 'order_by',
                startParam: 'offset',
                type: 'ajax',
                url: '/activities/history/' + activity_identifier
            },
            remoteSort: true
        });


        this.historyPanel = Ext.create('Ext.grid.Panel',{
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

        this.items = [{
            bodyPadding: 5,
            layout: 'card',
            margin: 3,
            itemId: 'activityDetailWizardPanel',
            items: [ this.centerPanel ],
            region: 'center',
            title: 'Details'
        },
        this.historyPanel
        ];

        this.title = 'Details on Activity ' + activity_identifier;

        this.callParent(arguments);
    },

    /**
     * Ext has some serious issues with panels collapsed on start. Instead, this
     * function is called right after showing this window.
     */
    _collapseHistoryPanel: function() {
        if (this.historyPanel) {
            this.historyPanel.collapse();
        }

        return this;
    },

    /**
     * Parameter activity is an instance of Lmkp.model.Activity
     */
    _populateDetails: function(activity, pendingVersion){

        if (activity) {

            // Set the current selection to current
            this.current = activity;
            this.centerPanel.currentActivity = activity;
            // Remove all existing panels
            this.centerPanel.removeAll();

			/**
			 * Function moved to StakeholderPanel on Sept. 9, 2012. If this 
			 * seems to work out, also delete function parameter pendingVersion
            // Show a notice if this version is a pending one
            if(pendingVersion) {
                this.centerPanel.add({
                    bodyCls: 'notice',
                    bodyPadding: 5,
                    html: 'You are seeing a pending version, which needs to be \n\
                        reviewed before it is publicly visible',
                    margin: '3 3 0 3'
                    
                });
            }
			 */

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
                comment_object: 'activity',
                identifier: activity.get('id'),
                margin: 3,
                xtype: 'lo_commentpanel'
            });
        }

        return activity;

    }
	
});
