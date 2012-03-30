Ext.define('Lmkp.controller.Main', {
    extend: 'Ext.app.Controller',

    views: [
        'Header',
        'Main',
        'SidePanel'
    ],
    
    stores: [
    	'Languages'
    ],

    init: function() {
        this.control({
            'viewport > panel': {
                render: this.onPanelRendered
            },
            'main toolbar combobox[id=language_combobox]': {
            	select: this.changeLanguage
            },
            'main toolbar combobox[id=profile_combobox]': {
            	select: this.changeProfile
            }
        });
    },
    
    changeProfile: function(combo, records, eOpts) {
    	console.log(records);
    	var form = Ext.create('Ext.form.Panel', {
            standardSubmit: true,
            url: '/'
        });
        form.submit({
            params: {
                _PROFILE_: records[0].get('field1')
            }
        });
    },
    
    changeLanguage: function(combo, records, eOpts) {
    	var form = Ext.create('Ext.form.Panel', {
            standardSubmit: true,
            url: '/'
        });
        form.submit({
            params: {
                _LOCALE_: records[0].get('locale')
            }
        });
    },

    onPanelRendered: function(comp) {
    	// load Language store
        this.getLanguagesStore().load();
        // set current language as selected in combobox
		var cb = Ext.ComponentQuery.query('combobox[id=language_combobox]')[0];
		cb.setValue(Lmkp.ts.msg("locale"));
    }
});
