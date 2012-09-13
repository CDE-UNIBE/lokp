/**
 * This is a STATIC store and is used to translate the predefined
 * Review Decision names (approved, rejected) from the database.
 * Any change made in the database needs to be added here as well.
 */

Ext.define('Lmkp.store.ReviewDecisions', {
    extend: 'Ext.data.Store',

    fields: ['id', 'name'],

    data: [
        {
            'id': 1,
            'name': Lmkp.ts.msg('reviewdecision-approved')
        }, {
            'id': 2,
            'name': Lmkp.ts.msg('reviewdecision-rejected')
        }
    ]
});