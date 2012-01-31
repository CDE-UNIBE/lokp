Ext.define('LMKP.view.MapPanel',{
    extend: 'GeoExt.panel.Map',
    alias: ['widget.mappanel'],

    initComponent: function(){
        console.log('MapPanel init');

        this.callParent(arguments);
    }
})