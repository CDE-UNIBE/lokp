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
        <title>Land Observatory</title>
        ## General Styles
        <link rel="stylesheet" type="text/css" href="/static/lib/extjs-4.1.1/resources/css/ext-all.css"></link>
        <link rel="stylesheet" type="text/css" href="${request.static_url('lmkp:static/style.css')}"></link>
        <script type="text/javascript" src="/static/lib/extjs-4.1.1/ext-debug.js"></script>
        <script type="text/javascript">
            Ext.Loader.setConfig({
                enabled: true,
                paths: {
                    'GeoExt': '/static/lib/geoext2/src/GeoExt/'
                }
            });
        </script>
        <script type="text/javascript" src="http://www.google.com/recaptcha/api/js/recaptcha_ajax.js"></script>
        <script type="text/javascript" src="/static/lib/OpenLayers-2.11/OpenLayers.js"></script>
        <!--script type="text/javascript" src="/static/lib/geoext2/src/GeoExt/GeoExt.js"></script-->
        <script type="text/javascript" src="/lang"></script>
        % if isinstance(has_permission('administer', request.context, request), ACLAllowed):
        <script type="text/javascript" src="/app/view/EditToolbar.js"></script>
        <script type="text/javascript" src="${request.static_url('lmkp:static/app/admin.js')}"></script>
        % elif isinstance(has_permission('moderate', request.context, request), ACLAllowed):
        <script type="text/javascript" src="/app/view/EditToolbar.js"></script>
        <script type="text/javascript" src="${request.static_url('lmkp:static/app/moderator.js')}"></script>
        % elif isinstance(has_permission('edit', request.context, request), ACLAllowed):
        <script type="text/javascript" src="/app/view/EditToolbar.js"></script>
        <script type="text/javascript" src="${request.static_url('lmkp:static/app/editor.js')}"></script>
        % else:
        <script type="text/javascript" src="/app/view/ViewToolbar.js"></script>
        <script type="text/javascript" src="${request.static_url('lmkp:static/app/public.js')}"></script>
        % endif
    </head>
    <body>
        <div id="header-div">
            <h1>Land Observatory</h1>
            <p>Some introductory text about the project etc.</p>
            <p>Maybe also a nice logo?</p>
        </div>
        <div id="main-div"></div>
    </body>
</html>