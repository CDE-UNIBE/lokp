/**
 * This is a STATIC store and is used to translate the predefined
 * Status names (pending, active, ...) from the database.
 * Any change made in the database needs to be added here as well.
 */

Ext.define('Lmkp.store.Status', {
	extend: 'Ext.data.Store',
	
	fields: ['db_name', 'display_name'],
	
	data: [
            {
		'db_name': 'pending',
		'display_name': Lmkp.ts.msg('status_pending')
            }, {
		'db_name': 'active',
		'display_name': Lmkp.ts.msg('status_active')
            }, {
		'db_name': 'inactive',
		'display_name': Lmkp.ts.msg('status_inactive')
            }, {
		'db_name': 'deleted',
		'display_name': Lmkp.ts.msg('status_deleted')
            }, {
		'db_name': 'rejected',
		'display_name': Lmkp.ts.msg('status_rejected')
            }, {
                'db_name': 'edited',
                'display_name': Lmkp.ts.msg('status_edited')
            }
        ]
});
