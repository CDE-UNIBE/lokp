<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"
      xmlns:tal="http://xml.zope.org/namespaces/tal"
      xmlns:i18n="http://xml.zope.org/namespaces/i18n"
      i18n:domain="pyramid_i18n_howto">
    <head>
        <title>${_("FORM TEST")}</title>
        <!-- Meta Tags -->
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <!-- CSS -->
        <link rel="stylesheet" href="/formstatic/css/beautify.css" type="text/css" />
        <link rel="stylesheet" href="/static/form.css" type="text/css" />
        <!-- JavaScript -->

        <!-- REQUIREMENTS -->
        <!-- CSS -->
        % for reqt in css_links:
            <link rel="stylesheet" href="/formstatic/${reqt}" type="text/css" />
        % endfor
        % for reqt in js_links:
            <script type="text/javascript" src="/formstatic/${reqt}"></script>
        % endfor
    </head>

    <body>
        <div id="form">
            <% context.write(form) %>
        </div>

        <script type="text/javascript">
           deform.load();
        </script>
    </body>
</html>