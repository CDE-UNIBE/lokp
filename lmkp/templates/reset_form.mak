<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <title>${_("Land Observatory")} - ${_(u"Login")}</title>
        <link rel="stylesheet" type="text/css" href="${request.static_url('lmkp:static/style.css')}"></link>
        <!--link rel="stylesheet" type="text/css" href="${request.static_url('lmkp:static/lib/extjs-4.1.1/resources/css/ext-standard.css')}"></link-->
        <script type="text/javascript" src="${request.static_url('lmkp:static/lib/extjs-4.1.1/ext.js')}"></script>
        <script type="text/javascript" src="${request.static_url('lmkp:static/lib/extjs-4.1.1/src/Ajax.js')}"></script>
        <script type="text/javascript">
            Ext.ns('Ext.ux');
            Ext.ux.process = function(){

                if(Ext.fly('reset-response-div')){
                    Ext.fly('reset-response-div').remove();
                }

                Ext.fly("body").createChild({
                    cls: 'login',
                    html: "Loading ...",
                    id: 'reset-loading-div',
                    tag: 'div'
                }, Ext.fly('reset-form-div'));

                //Ext.ux.loading(true);
                Ext.Ajax.request({
                    params: {
                        email: Ext.fly("email").getValue()
                    },
                    callback: function(options, success, response){
                        var r = Ext.decode(response.responseText);
                        Ext.fly("body").createChild({
                            cls: r.success ? 'login' : 'login login-warning',
                            html: r.msg,
                            id: 'reset-response-div',
                            tag: 'div'
                        }, Ext.fly('reset-form-div'));
                        if(Ext.fly('reset-loading-div')){
                            Ext.fly('reset-loading-div').remove();
                        }
                    },
                    url: '/reset'
                });
            }
        </script>
    </head>
    <body id="body">
        <div id="reset-header-div" class="login">
            <img src="${request.static_url('lmkp:static/img/lo-logo.png')}" alt="Land Observatory"/><br/>
            ${_(u"Reset password")}
        </div>
        <div id="reset-form-div">
            <form id="reset-form" action="javascript:Ext.ux.process();" method="POST">
                <fieldset class="simple_login">
                    <label for="email">${_(u"Email Address")}:</label>
                    <input class="simple_login" type="text" id="email" name="email" /><br />
                    <input type="hidden" name="came_from" value="${came_from}"/><br />
                    <input type="submit" name="form.submitted" value="Reset"/>
                </fieldset>
            </form>
        </div>
    </body>
</html>