Ext.define('Lmkp.view.manage.activities.Details',{
    extend: 'Ext.form.Panel',

    alias: [ 'widget.manageactivitiesdetails' ],

    buttons: [{
        text: 'Submit'
    }],

    defaults: {
        anchor: '100%'
    },

    defaultType: 'textfield',

    layout: 'anchor',

    /**
     * Items of this panel are loaded dynamically during application startup.
     */
    initComponent: function(){
        this.callParent(arguments);
    }
});