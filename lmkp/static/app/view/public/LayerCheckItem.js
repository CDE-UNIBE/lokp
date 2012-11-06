Ext.define('Lmkp.view.public.LayerCheckItem',{
    extend: 'Ext.container.Container',
    alias: ['widget.lo_layercheckitem'],

    config: {
        layer: null
    },

    layout: 'hbox',

    initComponent: function(){

        this.addEvents({
            'checkchange': true,
            'showlegend': true
        });

        var items = [{
            checked: this.checked,
            handler: function(checkbox, checked){
                this.fireEvent('checkchange', this, checked)
            },
            scope: this,
            xtype: 'checkbox'
        },{
            html: this.text,
            padding: '4 0 0 20',
            width: 250,
            xtype: 'container'
        },{
            handler: function(button, event){
                this.fireEvent('showlegend', this, this.layer);
            },
            scope: this,
            text: Lmkp.ts.msg('button_map_show-legend'),
            width: 100,
            xtype: 'button'
        }];

        this.items = items;

        this.callParent(arguments);
    }

});