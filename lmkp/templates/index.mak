<%

from pyramid.security import ACLAllowed
from pyramid.security import authenticated_userid
from pyramid.security import has_permission

%>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <title>Land Matrix Knowledge Platform</title>
        <link rel="stylesheet" type="text/css" href="/static/lib/ext-4.0.7-gpl/resources/css/ext-all.css"></link>
        <link rel="stylesheet" type="text/css" href="${request.static_url('lmkp:static/style.css')}"></link>
        <script type="text/javascript" src="/static/lib/ext-4.0.7-gpl/ext-debug.js"></script>
        <script type="text/javascript">
            Ext.Loader.setConfig({
                enabled: true,
                paths: {
                    'GeoExt': '/static/lib/GeoExt4/src',
                    'DyLmkp': '/app'
                }
            });
        </script>
        <script type="text/javascript" src="/static/lib/OpenLayers-2.11/OpenLayers.js"></script>
        <script type="text/javascript" src="/static/lib/GeoExt4/GeoExt.js"></script>
        <script type="text/javascript" src="/lang"></script>
        <%
        toolbarConfiguration = '/app/view/ViewToolbar.js'
        if isinstance(has_permission('edit', request.context, request), ACLAllowed):
            toolbarConfiguration = '/app/view/EditToolbar.js'
        %>
        <script type="text/javascript" src="${toolbarConfiguration}"></script>
        <script type="text/javascript" src="${request.static_url('lmkp:static/app/%s.js' % script)}"></script>
    </head>
    <body>
        <div id="header-div">
            <h1>${_("Welcome")}</h1>
            % if authenticated_userid(request) is not None:
            <div>
                <a href="/users/${request.user.username}">${request.user.username}</a>,
                <%block name="welcome_header">
                    ${_(u"Warmly welcome to the Land Matriz Knowledge Platformz!")}
                </%block>
                <br/>
                ${_(u"Unbelievable, you are logged in!")}
                <form action="/logout" method="post">
                    <fieldset>
                        <input type="hidden" name="came_from" value="/" />
                        <input type="submit" name="form.logout" value="Logout" />
                    </fieldset>
                </form>
            </div>
            % else:
            <div>
                <div>
                    ${welcome_header()}
                    <br/>${_(u"Please log in!")}
                </div>
                <form action="/login" method="POST">
                    <fieldset>
                        <input type="hidden" name="came_from" value="/"/>
                        Username: <input type="text" name="login" />
                        Password: <input type="password" name="password" />
                        <input type="submit" name="form.submitted" value="Login"/>
                    </fieldset>
                </form>
            </div>
            % endif
        </div>
        <div id="main-div"></div>
    </body>
</html>