Ext.define('Lmkp.controller.Outer', {
    extend: 'Ext.app.Controller',

    views: [
    'Main'
    ],

    stores: [
    'Languages',
    'Profiles'
    ],

    // needed because ext-debug.js does not contain Ext.util.Cookies
    // http://www.sencha.com/forum/showthread.php?187620-Ext.util.Cookies-is-undefined-while-using-ext-debug.js-file
    requires: [
    'Ext.util.Cookies'
    ],

    init: function() {
        this.control({
            'lo_logintoolbar combobox[id=language_combobox]': {
                select: this.onLanguageSelect
            },
            'lo_logintoolbar combobox[id=profile_combobox]': {
                select: this.onProfileSelect
            },
            'lo_logintoolbar button[id=login_submit]': {
                click: this.onLoginSubmit
            },
            'lo_logintoolbar button[id=logout_button]': {
                click: this.onLogout
            },
            'lo_logintoolbar button[id=user_button]': {
                click: this.onUserButtonClick
            }
        });
    },

    onLoginSubmit: function(button, event, eOpts){
        var username = Ext.ComponentQuery.query('toolbar textfield[id=username]')[0];
        var pw = Ext.ComponentQuery.query('toolbar textfield[id=password]')[0];
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

    onLogout: function(button, event, eOpts){
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

    onUserButtonClick: function(button, e, eOpts) {
        var win = Ext.create('Lmkp.view.users.UserWindow', {
            username: button.getText()
        });
        win.show();
    },

    onProfileSelect: function(combo, records, eOpts) {
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

    onLanguageSelect: function(combo, records, eOpts) {
        var form = Ext.create('Ext.form.Panel', {
            standardSubmit: true,
            url: '/'
        });
        form.submit({
            params: {
                _LOCALE_: records[0].get('locale')
            }
        });
    }


});