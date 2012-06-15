Ext.define('Lmkp.controller.Map',{
    extend: 'Ext.app.Controller',

    views: [
    'MapPanel'
    ],

    init: function(){
        this.control({
            'mappanel': {
                render: this.onPanelRendered
            }
        });
    },

    onPanelRendered: function(comp){
        var zoomBoxAction = Ext.create('GeoExt.Action',{
            control: comp.getZoomBoxControl(),
            map: comp.getMap(),
            iconCls: 'zoom-in-button',
            toggleGroup: 'map-controls'
        });
        console.log(zoomBoxAction);
        var tbar = comp.getDockedItems('toolbar')[0];
        console.log(tbar);
        tbar.add(Ext.create('Ext.button.Button',zoomBoxAction));
        tbar.add({
            text: "test",
            xtype: 'button'
        });
    }

    
})