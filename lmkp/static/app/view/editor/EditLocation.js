Ext.define('Lmkp.view.editor.EditLocation',{
    extend: 'Ext.window.Window',
    alias: ['widget.lo_editoreditlocationpanel'],

    config: {
        feature: null,
        selectCtrl: null
    },
    height: 150,
    modal: false,
    width: 200,

    initComponent: function() {
    
        var items = [{
            bodyPadding: 5,
            margin: 3,
            region: 'center',
            html: 'Move the Activity and press <b>Submit</b> when you\'re finished.',
            xtype: 'panel'
        },{
            handler: function(btn){
                this.hide();
                this.selectCtrl.unselectAll();
            },
            region: 'south',
            scope: this,
            text: 'Cancel',
            xtype: 'button'
        },{
            handler: function(btn){
                this.hide();

                var activities = {
                    activities: [{
                        id: this.feature.attributes.activity_identifier,
                        geometry: {
                            coordinates: [this.feature.geometry.x, this.feature.geometry.y],
                            type: 'Point'
                        },
                        taggroups: [],
                        version: this.feature.attributes.version
                    }]
                };

                Ext.Ajax.request({
                    failure: function(response){
                        Ext.Msg.alert("Failure", "Something went wrong");
                    },
                    jsonData: activities,
                    success: function(response){
                        Ext.Msg.alert("Success", "Activity has been uploaded");
                    },
                    url: '/activities'
                });
            },
            region: 'south',
            scope: this,
            text: 'Submit',
            xtype: 'button'
        }];
    
        this.items = [{
            layout: 'anchor',
            items: items,
            xtype: 'panel'
        }];
        
        
        this.callParent(arguments);
    }



});