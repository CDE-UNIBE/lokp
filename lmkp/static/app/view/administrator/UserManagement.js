Ext.define('Lmkp.view.administrator.UserManagement', {
    extend: 'Ext.form.Panel',

    alias: ['widget.lo_usermanagementpanel'],

    buttons: [{
        handler: function(button, event){
            var form = button.up('form').getForm();
            if (form.isValid()) {
                // Submit the Ajax request and handle the response
                form.submit({
                    success: function(form, response) {
                        var res = Ext.decode(response.response.responseText);
                        res.success ? Ext.Msg.alert('Success', res.msg) : Ext.Msg.alert('Failure', res.msg);
                        form.reset();
                    },
                    failure: function(form, response) {
                        var res = Ext.decode(response.response.responseText);
                        Ext.Msg.alert('Failed', res.msg ? res.msg : Lmkp.ts.msg("No response"));
                        form.reset();
                    }
                });
            }
        },
        text: 'Submit'
    }],
    defaults: {
        labelAlign: 'right',
        labelWidth: 120,
        margin: 3,
        width: 350
    },
    defaultType: 'textfield',
    formBind: true,
    items: [{
        allowBlank: false,
        fieldLabel: 'Username',
        name: 'username',
        regex: /^[a-zA-Z0-9\-\_\.]*$/,
        regexText: 'Not allowed special chars found.'
    },{
        allowBlank: false,
        fieldLabel: 'Password',
        inputType: 'password',
        name: 'password'
    },{
        allowBlank: false,
        fieldLabel: 'Email',
        name: 'email',
        regex: /.+\@.+\..+$/,
        regexText: 'Invalid email address.'
    },{
        allowBlank: false,
        editable: false,
        fieldLabel: Lmkp.ts.msg('User Group'),
        name: 'group',
        queryMode: 'local',
        store: [['administrators', Lmkp.ts.msg('Administrator')],
        ['moderators', Lmkp.ts.msg("Moderators")],
        ['editors', Lmkp.ts.msg("Editors")]],
        value: 'editors',
        xtype: 'combo'
    }],
    layout: 'vbox',
    method: 'POST',
    url: '/users/add'

});