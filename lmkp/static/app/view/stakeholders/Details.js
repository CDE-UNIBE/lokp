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
    'Lmkp.view.stakeholders.StakeholderPanel',
    'Lmkp.view.comments.CommentPanel'
    ],

    bbar: {
        items: ['->', {
            iconCls: 'cancel-button',
            itemId: 'closeWindowButton',
            scale: 'medium',
            text: 'Close', // also translate tooltip
            tooltip: 'Close window'
        }],
        xtype: 'toolbar'
    },

    initComponent: function(){

        this.centerPanel = Ext.create('Ext.panel.Panel',{
            region: 'center',
            autoScroll: true,
            layout: 'anchor',
            title: 'Details'
        });

        this.historyStore = Ext.create('Ext.data.Store', {
            autoLoad: true,
            autoScroll: true,
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
            remoteSort: true,

            proxy: {
                type: 'ajax',
                url: '/stakeholders/history/' + this.stakeholder.get('id'),
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
//            collapsed: true, -> Collapsing is done 'manually'
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

        this._populateDetails(this.stakeholder)

        this.items = [
        this.centerPanel,
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
    _populateDetails: function(stakeholder){

        if (stakeholder) {

            // Set the current selection to current
            this.current = stakeholder;

            // Remove all existing panels
            this.centerPanel.removeAll();

            // If there are no versions pending, simply show active version
            this.centerPanel.add({
                contentItem: stakeholder,
                border: 0,
                bodyPadding: 0,
                editable: true,
                hiddenOriginal: false,
                xtype: 'lo_stakeholderpanel'
            });

            // Add commenting panel
            this.centerPanel.add({
                comment_object: 'stakeholder',
                identifier: stakeholder.get('id'),
                xtype: 'lo_commentpanel'
            });
        }

        return stakeholder;

    }

});