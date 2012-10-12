Ext.define('Lmkp.utils.MessageBox', {
    extend: 'Ext.window.MessageBox',

    buttonText: {
        yes: Lmkp.ts.msg('button_yes'),
        no: Lmkp.ts.msg('button_no'),
        ok: Lmkp.ts.msg('button_ok'),
        cancel: Lmkp.ts.msg('button_cancel')
    }
});