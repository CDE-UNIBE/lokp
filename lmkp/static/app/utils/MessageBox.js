Ext.define('Lmkp.utils.MessageBox', {
    extend: 'Ext.window.MessageBox',

    buttonText: {
        yes: Lmkp.ts.msg('yes'),
        no: Lmkp.ts.msg('no'),
        ok: Lmkp.ts.msg('ok'),
        cancel: Lmkp.ts.msg('cancel')
    }
});