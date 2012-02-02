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

    items: [{
        fieldLabel: 'Details',
        name: 'details'

    },{
        fieldLabel: 'Details2',
        name: 'details2'

    }],

    layout: 'anchor',

    initComponent: function(){
        console.log('details');
        this.callParent(arguments);
    }
});