Ext.define('LMKP.controller.Main', {
    extend: 'Ext.app.Controller',

    views: [
        'Header',
        'Main'
    ],

    init: function() {
        this.control({
            'viewport > panel': {
                render: this.onPanelRendered
            }
        });
    },

    onPanelRendered: function() {
        // Do something
    }
});