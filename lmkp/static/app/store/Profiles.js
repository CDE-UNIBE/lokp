Ext.define('Lmkp.store.Profiles', {
    extend: 'Ext.data.Store',
    requires: 'Lmkp.model.Profile',
    model: 'Lmkp.model.Profile',

    data: Lmkp.available_profiles,

    proxy: {
        type: 'memory',
        reader: {
            type: 'json',
            root: 'data'
        }
    }

/**
	 * autoLoad disabled because it loads too late.
	 * The combobox (eg. in controller/Main.js) needs to know these values to set
	 * the current value as selected.
	 * 
	 * Use this.getProfilesStore().load() in controller to load store manually.
	 */
// autoLoad: true
});
