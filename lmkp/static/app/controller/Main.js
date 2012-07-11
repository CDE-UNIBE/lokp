Ext.define('Lmkp.controller.Main', {
    extend: 'Ext.app.Controller',

    views: [
    'moderator.Pending',
    'moderator.Main',
    'Filter',
    'Stakeholder',
    'editor.Map',
    'editor.Table'
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
            'viewport outerpanel,lo_publicpanel': {
                render: this.onPanelRendered
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
