/**
 * Subclass of Lmkp.view.items.Details window.
 */
Ext.define('Lmkp.view.stakeholders.Details',{
    extend: 'Lmkp.view.items.Details',
    alias: ['widget.lo_stakeholderdetailwindow'],

    centerPanelType: 'lo_stakeholderpanel',

    config: {
        centerPanel: null,
        historyPanel: null,
        historyStore: null
    },

    itemId: 'stakeholderDetailWindow',

    requires: [
    'Lmkp.view.stakeholders.StakeholderPanel'
    // For the time being, comments on Stakeholders are not yet supported.
    // 'Lmkp.view.comments.CommentPanel'
    ],

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
                    this._populateDetails(firstRecord);
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
                text: Lmkp.ts.msg('gui_version')
            }, {
                dataIndex: 'status',
                flex: 1,
                text: Lmkp.ts.msg('status_name')
            }, {
                dataIndex: 'timestamp',
                flex: 1,
                text: Lmkp.ts.msg('gui_timestamp')
            }],
            itemId: 'historyPanel',
            region: 'west',
            store: this.historyStore,
            title: Lmkp.ts.msg('gui_history'),
            width: 250
        });

        this.items = [{
            bodyPadding: 5,
            layout: 'card',
            margin: 3,
            itemId: 'stakeholderDetailWizardPanel',
            items: [ this.centerPanel ],
            region: 'center',
            title: Lmkp.ts.msg('gui_details')
        },
        this.historyPanel
        ];

        this.title = Lmkp.ts.msg('stakeholder_details-title') + ' ' + this.stakeholder.get('id');

        this.callParent(arguments);
    }
});