Ext.require('Ext.container.Viewport');
Ext.require('Ext.form.field.ComboBox');
Ext.require('Ext.form.FieldSet');
Ext.require('Ext.form.Label');
Ext.require('Ext.form.*');
Ext.require('Ext.fx.*');
Ext.require('Ext.grid.column.Template');
Ext.require('Ext.layout.container.Border');
Ext.require('Ext.layout.container.Column');
Ext.require('Ext.data.reader.Xml');
Ext.require('Ext.layout.container.Anchor');
Ext.require('Lmkp.grid.TransformGrid');
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

            // create the grid
            var grid = Ext.create('Lmkp.grid.TransformGrid', 'compare-table', {
                stripeRows: true,
                anchor: '100%',
                sortable: false,
                resizable: true,
                region: 'center',
                margin: 5
            });

            /*var grid = Ext.create('Ext.panel.Panel',{
                contentEl: 'compare-table',
                region: 'center'
            });*/

            var rdStore = Ext.create('Lmkp.store.ReviewDecisions').load();

            var type = Lmkp.type;

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
                    failure: function(form, response) {
                        Ext.Msg.show({
                            buttons: Ext.Msg.CANCEL,
                            icon: Ext.Msg.ERROR,
                            msg: response.response.responseText,
                            scope: this,
                            title: Lmkp.ts.msg('feedback_failure')
                        });
                    },
                    success: function(form, response) {
                        var returnJson = Ext.decode(response.response.responseText);
                        if(returnJson.success){
                            Ext.Msg.show({
                                buttons: Ext.Msg.OK,
                                fn: function(buttonId, text, opt){
                                    window.location.href = Lmkp.next_url;
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
                    value: Lmkp.identifier
                }, {
                    xtype: 'hiddenfield',
                    name: 'version',
                    value: Lmkp.current_version
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
                },grid,form]
            });
        }
    });
});