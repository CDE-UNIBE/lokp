Ext.define('Lmkp.view.stakeholders.Details',{
    extend: 'Ext.window.Window',
    alias: ['widget.lo_stakeholderdetailwindow'],

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

    itemId: 'stakeholderDetailWindow',

    layout: 'border',
    height: 400,
    width: 600,

    requires: [
    'Lmkp.view.stakeholders.StakeholderPanel'
    // For the time being, comments on Stakeholders are not yet supported.
    // 'Lmkp.view.comments.CommentPanel'
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

        this.centerPanel = Ext.create('Ext.panel.Panel',{
            autoScroll: true,
            layout: 'anchor',
            itemId: 'stakeholderDetailCenterPanel'
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
            'Lmkp.model.Stakeholder',
            'Lmkp.model.TagGroup',
            'Lmkp.model.Tag',
            'Lmkp.model.MainTag',
            'Lmkp.model.Involvement'
            ],

            model: 'Lmkp.model.Stakeholder',

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
                url: '/stakeholders/history/' + this.stakeholder.get('id')
            },
            remoteSort: true
        });

        this.historyPanel = Ext.create('Ext.grid.Panel',{
            // collapsed: true, -> Collapsing is done 'manually'
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
            itemId: 'stakeholderDetailWizardPanel',
            items: [ this.centerPanel ],
            region: 'center',
            title: 'Details'
        },
        this.historyPanel
        ];

        this.title = 'Details on Stakeholder ' + this.stakeholder.get('id');

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
    },

    /**
     * Parameter stakeholder is an instance of Lmkp.model.Stakeholder
     */
    _populateDetails: function(stakeholder, pendingVersion){

        if (stakeholder) {

            // Set the current selection to current
            this.current = stakeholder;

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
                contentItem: stakeholder,
                border: 0,
                bodyPadding: 0,
                editable: true,
                hiddenOriginal: false,
                xtype: 'lo_stakeholderpanel'
            });

            // Add commenting panel. For now (Sept. 9, 2012), comments on 
            // Stakeholders are not yet supported.
            // this.centerPanel.add({
                // comment_object: 'stakeholder',
                // identifier: stakeholder.get('id'),
                // xtype: 'lo_commentpanel'
            // });
        }

        return stakeholder;

    }

});