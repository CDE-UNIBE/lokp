Ext.define('Lmkp.controller.Main', {
    extend: 'Ext.app.Controller',

    views: [
        'Header',
        'Main',
        'SidePanel'
    ],

    init: function() {
        this.control({
            'viewport > panel': {
                render: this.onPanelRendered
            }
        });
    },

    onPanelRendered: function(comp) {
        // do something
    }
});
