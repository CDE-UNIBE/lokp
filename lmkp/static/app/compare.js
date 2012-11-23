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

            var uidRegExp = /(activities|stakeholders)\/compare\/[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}\/[0-9]+\/[0-9]+/gi;

            var urlParts = uidRegExp.exec(window.location.href)[0].split('/');

            var uid = urlParts[2];
            var ref_version = urlParts[3];
            var new_version = urlParts[4];
            
            var oldVersionCombo = Ext.create('Ext.form.field.ComboBox',{
                fieldLabel: Lmkp.ts.msg('Reference Version:'),
                labelWidth: 150,
                queryMode: 'local',
                store: Lmkp.available_versions,
                value: ref_version
            });

            var newVersionCombo = Ext.create('Ext.form.field.ComboBox',{
                fieldLabel: Lmkp.ts.msg('Comparison Version:'),
                labelWidth: 150,
                queryMode: 'local',
                store: Lmkp.available_versions,
                style: {
                    'margin-left': '15px'
                },
                value: new_version
            });
            
            var diffButton = Ext.create('Ext.button.Button',{
                handler: function(button, event){
                    var refVersion = oldVersionCombo.getValue();
                    var newVersion = newVersionCombo.getValue();
                    window.location.href = Lmkp.compare_url + "/" + refVersion + "/" + newVersion
                },
                style: {
                    'margin-left': '15px'
                },
                text: Lmkp.ts.msg("Show differences"),
                xtype: 'button'
            });

            // create the grid
            var grid = Ext.create('Lmkp.grid.TransformGrid', 'compare-table', {
                stripeRows: true,
                anchor: '100%',
                sortable: false,
                resizable: true,
                region: 'center',
                margin: 5,
                tbar: [oldVersionCombo, newVersionCombo, '->', diffButton]
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
                },grid,{
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
