Ext.require('Ext.container.Viewport');
Ext.require('Ext.data.JsonStore');
Ext.require('Ext.form.field.ComboBox');
Ext.require('Ext.form.field.Hidden');
Ext.require('Ext.form.Label');
Ext.require('Ext.form.Panel');
Ext.require('Ext.fx.*');
Ext.require('Ext.grid.Panel');
Ext.require('Ext.layout.container.Border');
Ext.require('Ext.toolbar.Paging');
Ext.require('Ext.util.*');
Ext.require('Lmkp.controller.login.Toolbar');
Ext.require('Lmkp.store.ReviewDecisions');
Ext.require('Lmkp.view.login.Toolbar');

Ext.onReady(function(){

    /**
     * This is probably not needed anymore!
     */
    console.log("Don't delete me!!!");

    var loadingMask = Ext.get('loading-mask');
    loadingMask.fadeOut({
        duration: 1000,
        remove: true
    });

    Ext.application({
        name: 'Lmkp',
        appFolder: '/static/app',

        requires: [
        'Lmkp.view.login.Toolbar'
        ],

        controllers: [
        'activities.NewActivity',
        'login.Toolbar'
        ],

        launch: function() {

            var me = this;

            var uidRegExp = /(activities|stakeholders)\/review\/[a-zA-Z]+\/[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}(\/[0-9]+\/[0-9]+)*/gi;

            var urlParts = uidRegExp.exec(window.location.href)[0].split('/');

            var type = urlParts[0];
            var format = urlParts[2];
            var uid = urlParts[3];
            var ref_version = urlParts[4] ? urlParts[4] : 1;
            var new_version = urlParts[5] ? urlParts[5] : 1;

            var urlTemplate = new Ext.Template("/{0}/review/{1}/{2}");
            urlTemplate.apply([type, format, uid, ref_version, new_version]);

            var reloadStores = function() {
                var url = urlTemplate.apply([type, 'json', uid]);

                taggroupGrid.setLoading(true);
                involvementGrid.setLoading(true);
                Ext.Ajax.request({
                    url: url,
                    success: function(response){
                        var text = response.responseText;
                        var data = Ext.decode(text);
                        taggroupStore.loadRawData(data);
                        involvementStore.loadRawData(data);

                        // Set the new version to the hidden field
                        var versionfield = form.down('hiddenfield[name="version"]');
                        versionfield.setValue(data.metadata.version);

                        var reconf = [{
                            flex: 1,
                            text: data.metadata.active_title,
                            dataIndex: 'ref',
                            renderer: taggroupRenderer
                        },{
                            flex: 1,
                            text: data.metadata.pending_title,
                            dataIndex: 'new',
                            renderer: taggroupRenderer
                        }];

                        involvementGrid.reconfigure(null, reconf);

                        taggroupGrid.reconfigure(null, reconf);

                        if(!data.metadata.version){
                            form.disable();
                        }

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

            var editCurrentVersion = function(form, response){
                Ext.Msg.show({
                    buttons: Ext.Msg.CANCEL,
                    icon: Ext.Msg.ERROR,
                    msg: response.response.responseText,
                    scope: this,
                    title: Lmkp.ts.msg('feedback_failure')
                });

//                var store = Ext.create('Ext.data.Store', {
//                    autoLoad: true,
//                    listeners: {
//                        'load': function(store, records, successful){
//                            var c = me.getController('activities.NewActivity');
//                            c.showNewActivityWindow(records[0]);
//                        }
//                    },
//                    model: 'Lmkp.model.Activity',
//                    proxy: {
//                        reader: {
//                            root: 'data',
//                            type: 'json'
//                        },
//                        type: 'ajax',
//                        url : '/' + type + '/json/' + uid
//                    }
//                });

               
            }

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

            var refreshButton = Ext.create('Ext.button.Button',{
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
                tbar: ['->', refreshButton]
            });

            var rdStore = Ext.create('Lmkp.store.ReviewDecisions').load();

            var submitButton = Ext.create('Ext.button.Button',{
                iconCls: 'save-button',
                itemId: 'reviewSubmitButton',
                name: 'review_submit',
                scale: 'medium',
                store_type: type, // helper parameter
                text: Lmkp.ts.msg('button_submit'),
                xtype: 'button'
            });

            submitButton.on('click', function(button, event, eOpts){
                form.submit({
                    failure: editCurrentVersion,
                    success: function(form, response) {
                        var returnJson = Ext.decode(response.response.responseText);
                        if(returnJson.success){
                            Ext.Msg.show({
                                buttons: Ext.Msg.OK,
                                fn: function(buttonId, text, opt){
                                    reloadStores();
                                },
                                icon: Ext.Msg.INFO,
                                msg: returnJson.msg,
                                scope: this,
                                title: Lmkp.ts.msg('feedback_success')
                            });
                        } else {
                            Ext.Msg.show({
                                buttons: Ext.Msg.CANCEL,
                                icon: Ext.Msg.ERROR,
                                msg: returnJson.msg,
                                scope: this,
                                title: Lmkp.ts.msg('feedback_failure')
                            });
                        }
                    }
                });
            });

            var form = Ext.create('Ext.form.Panel',{
                buttons: [submitButton],
                buttonAlign: 'right',
                items: [{
                    store: rdStore,
                    name: 'review_decision',
                    queryMode: 'local',
                    displayField: 'name',
                    valueField: 'id',
                    fieldLabel: Lmkp.ts.msg('moderator_review-decision'),
                    allowBlank: false,
                    flex: 1,
                    margin: 3,
                    value: 1,
                    width: 400,
                    xtype: 'combobox'
                }, {
                    fieldLabel: Lmkp.ts.msg('moderator_review-comment'),
                    margin: 3,
                    name: 'comment_textarea',
                    width: 400,
                    xtype: 'textarea'
                }, {
                    xtype: 'hiddenfield',
                    name: 'identifier',
                    value: uid
                }, {
                    xtype: 'hiddenfield',
                    name: 'version',
                    value: Lmkp.version
                }],
                region: 'south',
                style: {
                    margin: '0px 5px 5px'
                },
                url: '/' + type + '/review',
                xtype: 'form'
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
                },centerContainer,form,{
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