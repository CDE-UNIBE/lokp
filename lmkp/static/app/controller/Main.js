Ext.define('Lmkp.controller.Main', {
    extend: 'Ext.app.Controller',

    views: [
        'Header',
        'Main',
        'Filter',
        'Stakeholder',
        'MapPanel'
    ],
    
    stores: [
    	'Languages',
    	'Profiles',
    	'ActivityGrid',
        'StakeholderGrid'
    ],
    
    // needed because ext-debug.js does not contain Ext.util.Cookies
    // http://www.sencha.com/forum/showthread.php?187620-Ext.util.Cookies-is-undefined-while-using-ext-debug.js-file
    requires: [
    	'Ext.util.Cookies'
    ],

    init: function() {
        this.control({
            'viewport > main': {
                render: this.onPanelRendered
            },
            'main toolbar combobox[id=language_combobox]': {
            	select: this.changeLanguage
            },
            'main toolbar combobox[id=profile_combobox]': {
            	select: this.changeProfile
            },
            'main toolbar button[id=login_submit]': {
            	click: this.loginSubmit
            },
            'main toolbar button[id=logout_button]': {
            	click: this.logout
            },
            'main toolbar button[id=user_button]': {
            	click: this.showUserWindow
            }
        });
    },
    
    showUserWindow: function(button, e, eOpts) {
    	var win = Ext.create('Lmkp.view.users.UserWindow', {
    		username: button.getText()
    	});
    	win.show();
    },
    
    logout: function() {
    	var form = Ext.create('Ext.form.Panel', {
    		standardSubmit: true,
    		url: '/logout'
    	});
    	form.submit({
    		params: {
	    		'form.logout': true
    		}
    	});
    },
    
    loginSubmit: function() {
    	var username = Ext.ComponentQuery.query('main toolbar textfield[id=username]')[0];
    	var pw = Ext.ComponentQuery.query('main toolbar textfield[id=password]')[0];
    	if (username.getValue() != '' && pw.getValue() != '') {
	    	var form = Ext.create('Ext.form.Panel', {
	    		standardSubmit: true,
	    		url: '/login'
	    	});
	    	form.submit({
	    		params: {
	    			'form.submitted': true,
	    			login: username.getValue(),
	    			password: pw.getValue()
	    		}
	    	});
    	}
    },

    changeProfile: function(combo, records, eOpts) {
    	var form = Ext.create('Ext.form.Panel', {
            standardSubmit: true,
            url: '/'
        });
        form.submit({
            params: {
                _PROFILE_: records[0].get('profile')
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
		var lang_cb = Ext.ComponentQuery.query('combobox[id=language_combobox]')[0];
		lang_cb.setValue(Lmkp.ts.msg("locale"));
		
		// load profile store
        this.getProfilesStore().load();
      	// get current profile (default: global)
      	var profile = Ext.util.Cookies.get('_PROFILE_');
      	if (!profile) {
      		profile = 'global'
      	}
      	// set current profile as selected in combobox
        var profile_cb = Ext.ComponentQuery.query('combobox[id=profile_combobox]')[0];
        profile_cb.setValue(profile);
        
        // load activity grid store
        this.getActivityGridStore().load();
    }
});
