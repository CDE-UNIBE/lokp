<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
    <head>

        <%
            if 'scripts/jquery-ui-1.8.11.custom.min.js' not in js_links:
                js_links.append('scripts/jquery-ui-1.8.11.custom.min.js')
        %>

        % for reqt in js_links:
            <script type="text/javascript" src="/formstatic/${reqt}"></script>
        % endfor

        <script type="text/javascript" src="/custom/js/vendor/bootstrap.min.js"></script>
    </head>

    <body>

        <div id="fileUploadForm">
            ${form | n}
        </div>

        <script type="text/javascript">
            deform.load();
        </script>
    </body>
</html>

