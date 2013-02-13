Ext.define('Lmkp.view.administrator.UserManagement', {
    extend: 'Ext.form.Panel',

    alias: ['widget.lo_usermanagementpanel'],

    buttons: [{
        handler: function(button, event){
            var form = button.up('form').getForm();
            if (form.isValid()) {
                // Submit the Ajax request and handle the response
                form.submit({
                    url: '/users/add',
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
        submitValue: false,
        fieldLabel: 'Password',
        inputType: 'password',
        itemId: 'passwordField'
    },{
        allowBlank: false,
        fieldLabel: 'Retype password',
        inputType: 'password',
        name: 'password',
        validator: function(value){
            var pw = this.previousSibling('[itemId="passwordField"]');
            if(pw.getValue() == value){
                return true;
            }
            return "Password does not match.";
        }
    },{
        allowBlank: false,
        fieldLabel: 'Email',
        name: 'email',
        regex: /.+\@.+\..+$/,
        regexText: 'Invalid email address.'
    },{
        xtype: 'checkboxgroup',
        fieldLabel: Lmkp.ts.msg('User Groups'),
        columns: 1,
        vertical: true,
        items: [
            {
                boxLabel: Lmkp.ts.msg('usergroup_editors'),
                inputValue: 'editors',
                name: 'groups',
                checked: true,
                readOnly: true
            }, {
                boxLabel: Lmkp.ts.msg('usergroup_moderators'),
                inputValue: 'moderators',
                name: 'groups'
            }, {
                boxLabel: Lmkp.ts.msg('usergroup_administrators'),
                inputValue: 'administrators',
                name: 'groups'
            }, {
                boxLabel: Lmkp.ts.msg('usergroup_translators'),
                inputValue: 'translators',
                name: 'groups'
            }
        ]
    }],
    layout: 'vbox',
    method: 'POST'
});