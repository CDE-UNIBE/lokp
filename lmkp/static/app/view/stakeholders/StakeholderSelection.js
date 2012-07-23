Ext.define('Lmkp.view.stakeholders.StakeholderSelection', {
    extend: 'Ext.window.Window',

    alias: ['widget.lo_stakeholderselection'],

    config: {
        selectedStakeholder: {}
    },

    layout: 'border',

    height: 600,

    width: 400,

    tplMarkup: '<div><ul><li><b>{name}</b></li><li>{id}</li></ul></div>',

    initComponent: function(){

        var store = Ext.create('Ext.data.Store', {
            requires: ['Lmkp.model.Stakeholder',
            'Lmkp.model.TagGroup',
            'Lmkp.model.Tag',
            'Lmkp.model.MainTag',
            'Lmkp.model.Point'
            ], // all are needed to build relation
            model: 'Lmkp.model.Stakeholder',

            pageSize: 10,

            proxy: {
                extraParams: {
                    sh__queryable: Lmkp.ts.msg("stakeholder-name")
                },
                type: 'ajax',
                url: '/stakeholders',
                reader: {
                    root: 'data',
                    type: 'json',
                    totalProperty: 'total'
                },
                startParam: 'offset'
            }
        });

        this.detailTpl = Ext.create(Ext.Template, this.tplMarkup);

        this.items = [];
        
        this.items.push({
            tpl: this.detailTpl,
            itemId: 'detailpanel',
            region: 'south',
            height: 100,
            xtype: 'panel'
        });
        
        var formpanel = Ext.create('Ext.form.Panel', {
            items: [{
                displayField: 'id',
                // Template for the content inside text field
                displayTpl: Ext.create('Ext.XTemplate',
                    '<tpl for=".">',
                    '{id}',
                    '</tpl>'
                    ),
                fieldLabel: 'Name',
                hideTrigger: true,
                itemId: 'Name__textfield',
                listConfig: {

                    prepareData: function(data, recordIndex, record){
 
                        var name = record.getTagValues(Lmkp.ts.msg('stakeholder-name'));
                        if(name.length == 0){
                            name = ['Unknown'];
                        }

                        return {
                            'id': record.id,
                            'version': record.version,
                            'name': name.join(',')
                        }
                    }


                },
                minChar: 3,
                queryMode: 'remote',
                queryParam: 'sh__' + Lmkp.ts.msg("stakeholder-name") + '__ilike',
                remoteFilter: true,
                store: store,
                tpl: Ext.create('Ext.XTemplate',
                    '<tpl for=".">',
                    '<div class="x-boundlist-item">{name}</div>',
                    '</tpl>'
                    ),
                typeAhead: true,
                valueField: 'id',
                xtype: 'combo'
            },{
                fieldLabel: 'Country',
                itemId: 'Country__textfield',
                xtype: 'textfield'
            }],
            region: 'center'
        });

        this.items.push(formpanel);

        this.callParent(arguments);
    },

    onRowSelect: function(model, selected){
        this.selectedStakeholder = selected[0];

        // Find a name
        var name = Lmkp.ts.msg("unknown");
        for(var i = 0; i < this.selectedStakeholder.taggroups().getCount(); i++){

            var taggroup = this.selectedStakeholder.taggroups().getAt(i);
            for(var j = 0; j < taggroup.tags().getCount(); j++) {
                var tag = taggroup.tags().getAt(j);
                if(tag.get('key') == Lmkp.ts.msg("stakeholder-name")) {
                    name = tag.get('value');
                }
            }
        }

        var detailPanel = this.getComponent('detailpanel');
        this.detailTpl.overwrite(detailPanel.body, {
            name: name,
            id: this.selectedStakeholder.get('id')
        });
    }


});