Ext.require('Ext.container.Viewport');
Ext.require('Ext.data.JsonStore');
Ext.require('Ext.form.field.ComboBox');
Ext.require('Ext.form.FieldSet');
Ext.require('Ext.form.Label');
Ext.require('Ext.form.*');
Ext.require('Ext.fx.*');
Ext.require('Ext.grid.column.Template');
Ext.require('Ext.grid.Panel');
Ext.require('Ext.layout.container.Anchor');
Ext.require('Ext.layout.container.Border');
Ext.require('Ext.layout.container.Column');
Ext.require('Ext.panel.Table');
Ext.require('Ext.selection.RowModel');
Ext.require('Ext.view.Table');
Ext.require('Lmkp.controller.login.Toolbar');
Ext.require('Lmkp.view.login.Toolbar');

Ext.onReady(function(){
    var loadingMask = Ext.get('loading-mask');
    loadingMask.fadeOut({
        duration: 1000,
        remove: true
    });

    Ext.application({
        name: 'Lmkp',
        appFolder: '../../static/app',

        requires: [
        'Lmkp.view.login.Toolbar'
        ],

        controllers: [
        'login.Toolbar'
        ],

        launch: function() {

            var uidRegExp = /(activities|stakeholders)\/compare\/[a-zA-Z]+\/[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}(\/[0-9]+\/[0-9]+)*/gi;

            var urlParts = uidRegExp.exec(window.location.href)[0].split('/');

            var type = urlParts[0];
            var format = urlParts[2];
            var uid = urlParts[3];
            var ref_version = urlParts[4] ? urlParts[4] : 1;
            var new_version = urlParts[5] ? urlParts[5] : 1;

            var urlTemplate = new Ext.Template("/{0}/compare/{1}/{2}/{3}/{4}");
            urlTemplate.apply([type, format, uid, ref_version, new_version]);

            var reloadStores = function() {
                ref_version = oldVersionCombo.getValue();
                new_version = newVersionCombo.getValue();

                // Update the permalink button URL
                var aEl = Ext.query('#permalink-button a')[0];
                aEl.href = urlTemplate.apply([type, 'html', uid, ref_version, new_version]);

                taggroupGrid.setLoading(true);
                involvementGrid.setLoading(true);
                Ext.Ajax.request({
                    url: urlTemplate.apply([type, 'json', uid, ref_version, new_version]),
                    success: function(response){
                        var text = response.responseText;
                        var data = Ext.decode(text);
                        taggroupStore.loadRawData(data);
                        involvementStore.loadRawData(data);

                        var reconf = [{
                            flex: 1,
                            text: data.metadata.ref_title,
                            dataIndex: 'ref',
                            renderer: taggroupRenderer
                        },{
                            flex: 1,
                            text: data.metadata.new_title,
                            dataIndex: 'new',
                            renderer: taggroupRenderer
                        }];

                        involvementGrid.reconfigure(null, reconf);

                        taggroupGrid.reconfigure(null, reconf);

                    }
                });
            }

            var taggroupRenderer = function(value, metaData, record) {
                metaData.tdCls = value.class;

                var html = "";
                for(var i = 0; i < value.tags.length; i++){
                    var tag = value.tags[i];
                    var prefix = "";
                    if(value.class == 'add' || value.class == 'add involvement'){
                        prefix += "+ ";
                    } else if(value.class == 'remove' || value.class == 'remove involvement'){
                        prefix += "- ";
                    }
                    html += "<div>" + prefix + tag.key + ": " + tag.value + "</div>";
                }

                return html;
            }
            
            var oldVersionCombo = Ext.create('Ext.form.field.ComboBox',{
                editable: false,
                fieldLabel: Lmkp.ts.msg('gui_version') + ":",
                //labelWidth: 150,
                listeners: {
                    select: function(combo){
                        reloadStores();
                    }
                },
                queryMode: 'local',
                store: Lmkp.available_versions,
                value: ref_version
            });

            var newVersionCombo = Ext.create('Ext.form.field.ComboBox',{
                editable: false,
                fieldLabel: Lmkp.ts.msg('gui_version') + ":",
                //labelWidth: 150,
                listeners: {
                    select: function(combo){
                        reloadStores();
                    }
                },
                region: 'center',
                queryMode: 'local',
                store: Lmkp.available_versions,
                value: new_version
            });
            
            var diffButton = Ext.create('Ext.button.Button',{
                handler: function(button, event){
                    reloadStores();
                },
                iconAlign: 'top',
                iconCls: 'button-refresh',
                scale: 'medium',
                text: Lmkp.ts.msg('Refresh'),
                tooltip: Lmkp.ts.msg('Refresh'),
                xtype: 'button'
            });

            var permalinkButton = Ext.create('Ext.button.Button',{
                id: 'permalink-button',
                href: urlTemplate.apply([type, format, uid, oldVersionCombo.getValue(), newVersionCombo.getValue()]),
                hrefTarget: '',
                region: 'east',
                iconAlign: 'top',
                iconCls: 'button-link',
                text: Lmkp.ts.msg("Link"),
                tooltip: Lmkp.ts.msg("Permanent link to current view"),
                scale: 'medium',
                xtype: 'button'
            });

            var taggroupStore = Ext.create('Ext.data.JsonStore', {
                autoLoad: false,
                fields:['ref', 'new'],
                listeners: {
                    'load': function(store, records, successful, eOpts){
                        taggroupGrid.setLoading(false);
                    }
                },
                proxy: {
                    type: 'ajax',
                    reader: {
                        type: 'json',
                        root: 'taggroups'
                    },
                    url: urlTemplate.apply([type, 'json', uid, ref_version, new_version])
                }
            });

            var involvementStore = Ext.create('Ext.data.JsonStore', {
                autoLoad: false,
                fields:['ref', 'new'],
                listeners: {
                    'load': function(store, records, successful, eOpts){
                        involvementGrid.setLoading(false);
                    }
                },
                proxy: {
                    type: 'ajax',
                    reader: {
                        type: 'json',
                        root: 'involvements'
                    },
                    url: urlTemplate.apply([type, 'json', uid, ref_version, new_version])
                }
            });

            var taggroupGrid = Ext.create('Ext.grid.Panel', {
                border: 0,
                columns: [{
                    flex: 1,
                    dataIndex: 'ref',
                    renderer: taggroupRenderer
                },{
                    flex: 1,
                    dataIndex: 'new',
                    renderer: taggroupRenderer
                }],
                flex: 1,
                listeners: {
                    'render': function(comp, eOpts){
                        comp.setLoading(true);
                    } 
                },
                region: 'center',
                store: taggroupStore,
                title: Lmkp.ts.msg('Taggroups')
            });

            var involvementGrid = Ext.create('Ext.grid.Panel', {
                border: 0,
                columns: [{
                    flex: 1,
                    dataIndex: 'ref',
                    renderer: taggroupRenderer
                },{
                    flex: 1,
                    dataIndex: 'new',
                    renderer: taggroupRenderer
                }],
                flex: 1,
                listeners: {
                    'render': function(comp, eOpts){
                        comp.setLoading(true);
                    }
                },
                region: 'south',
                split: true,
                store: involvementStore,
                title: Lmkp.ts.msg('involvements_title')
            });

            var centerContainer = Ext.create('Ext.panel.Panel',{
                items: [
                taggroupGrid,
                involvementGrid
                ],
                layout: 'border',
                listeners: {
                    'render': function(comp, eOpts){
                        reloadStores();
                    }
                },
                region: 'center',
                style: {
                    margin: '5px'
                },
                dockedItems: [{
                    dock: 'top',
                    layout: {
                        align: 'stretchmax',
                        type: 'hbox'
                    },
                    items: [{
                        border: 0,
                        flex: 1,
                        items: [oldVersionCombo],
                        xtype: 'toolbar'
                    },{
                        border: 0,
                        flex: 1,
                        items: [newVersionCombo, '->', diffButton, permalinkButton],
                        xtype: 'toolbar'
                    }],
                    xtype: 'container'
                }]
            });

            Ext.create('Ext.container.Viewport', {
                border: false,
                layout: {
                    type: 'border',
                    padding: 0
                },
                items: [{
                    region: 'north',
                    xtype: 'lo_logintoolbar'
                },{
                    autoScroll: true,
                    contentEl: 'header-div',
                    height: 105,
                    region: 'north',
                    xtype: 'panel'
                },centerContainer,{
                    height: 30,
                    contentEl: 'social-plugin',
                    region: 'south',
                    style: {
                        'margin-left': '5px'
                    },
                    xtype: 'container'
                }]
            });


        }
    });
});
