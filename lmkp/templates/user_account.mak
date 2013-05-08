<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
      xmlns:tal="http://xml.zope.org/namespaces/tal"
      xmlns:i18n="http://xml.zope.org/namespaces/i18n"
      i18n:domain="pyramid_i18n_howto">
    <head>
        <title>${_("User Account")}</title>
        <!-- Meta Tags -->
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <!-- CSS -->
        <!--link rel="stylesheet" href="/formstatic/css/beautify.css" type="text/css" />
        <link rel="stylesheet" href="/static/form.css" type="text/css" /-->
        <style type="text/css">
            div.login {
                border: 1px solid silver;
                padding: 10px;
                width: 600px;
                margin: 0 auto;
                margin-bottom: 5px;
                margin-top: 5px;
                font-family: Arial, sans-serif;
                font-size: 12px;
                text-align: center;
            }
            select, input {
                margin-left: 30px;
            }
            .error {
                background-color: #F68E1D;
            }
        </style>
        <!-- JavaScript -->

        <!-- REQUIREMENTS -->
        <!-- CSS -->
        % for reqt in css_links:
        <!--link rel="stylesheet" href="/formstatic/${reqt}" type="text/css" /-->
        % endfor
        % for reqt in js_links:
        <script type="text/javascript" src="/formstatic/${reqt}"></script>
        % endfor
    </head>

    <body>
        <div class="login">
            <a href="/">
                <img src="${request.static_url('lmkp:static/img/lo-logo.png')}" alt="${_(u'Land Observatory')}"/>
            </a><br/>
            ${_(u"Update user settings")}
        </div>
        <div id="form" class="login" style="text-align: left;">
            <% context.write(form) %>
        </div>

        <script type="text/javascript">
            deform.load();
        </script>
    </body>
</html>