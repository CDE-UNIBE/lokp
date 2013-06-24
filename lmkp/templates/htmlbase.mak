
<!DOCTYPE html>
<!--[if lt IE 7]>      <html class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]>         <html class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]>         <html class="no-js lt-ie9"> <![endif]-->
<!--[if gt IE 8]><!--> <html class="no-js"> <!--<![endif]-->
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <title>
            <%
                try:
                    self.title()
                except AttributeError:
                    context.write("Land Observatory")
            %>
        </title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width">

        <link rel="stylesheet" href="${request.static_url('lmkp:static/media/css/bootstrap-combined.no-icons.min.css')}">
        <link rel="stylesheet" href="${request.static_url('lmkp:static/media/css/font-awesome/css/font-awesome.css')}">

        <link rel="stylesheet" href="${request.static_url('lmkp:static/media/css/bootstrap-responsive.min.css')}">
        <link rel="stylesheet" href="${request.static_url('lmkp:static/media/css/main.css')}">

        <link rel="stylesheet" href="${request.static_url('lmkp:static/media/css/custom.css')}">

        <script src="${request.static_url('lmkp:static/media/js/vendor/modernizr-2.6.2-respond-1.1.0.min.js')}"></script>

        <style type="text/css">
            .header-select {
                border: 0px;
                color: black;
                font-size: 0.8em;
                height: 22px;
                width: 100px;
            }
            .blacktemp {
                color: black;
                margin: 0 7px;
                text-decoration: underline;
            }
            .blacktemp .caret {
                border-top-color: black !important;
            }
            .logouttemp {
                color: black;
                text-decoration: underline;
            }
        </style>

        ## Include the head tags of the child template if available.
        <%
            try:
                self.head_tags()
            except AttributeError:
                pass
        %>

    </head>
    <body>
        <!--[if lt IE 7]>
            <p class="chromeframe">You are using an <strong>outdated</strong> browser. Please <a href="http://browsehappy.com/">upgrade your browser</a> or <a href="http://www.google.com/chromeframe/?redirect=true">activate Google Chrome Frame</a> to improve your experience.</p>
        <![endif]-->

        <div class="wrap">
            <div id="main" class="clearfix">

                ## Header

                <div class="navbar header_self">
                    <div class="container">
                        <div class="logo">
                            <a href="${request.route_url('index')}">
                                <img src="${request.static_url('lmkp:static/media/img/logo.png')}" />
                            </a>
                        </div>
                            <div class="top_menu">
                                <ul class="top-menu">
                                    <%
                                        # The entries of the top menus as arrays
                                        # with
                                        # - url
                                        # - icon (li class)
                                        # - name
                                        topmenu = [
                                            [request.route_url('map_view'), 'icon-map-marker', 'Map'],
                                            [request.route_url('grid_view'), 'icon-align-justify', 'Grid'],
                                            [request.route_url('charts_view'), 'icon-bar-chart', 'Charts']
                                        ]
                                    %>

                                    % for t in topmenu:
                                        <li
                                            % if t[0] == request.current_route_url():
                                                class="active grid"
                                            % endif
                                            >
                                            <a href="${t[0]}">
                                                <i class="${t[1]}"></i>&nbsp;&nbsp;${t[2]}
                                            </a>
                                        </li>
                                    % endfor
                                </ul>
                            </div>
                            <div class="user">
                                <ul class="nav nav-pills">
                                            % if request.user is None:
                                                <li class="active">
                                                    <div>
                                                        <a class="blacktemp" href="${request.route_url('login_form')}">
                                                            Login
                                                        </a>
                                                    </div>
                                                </li>
                                            % else:
                                                <li>
                                                    <div>
                                                        ${request.user.username} (<a href="${request.route_url('logout')}" class="logouttemp">Logout</a>)&nbsp;&nbsp;
                                                    </div>
                                                </li>
                                            % endif

                                    <li>|</li>
                                    <%
                                        from lmkp.views.translation import get_languages
                                        languages = get_languages()
                                        selectedlanguage = languages[0]
                                        for l in languages:
                                            if locale == l[0]:
                                                selectedlanguage = l
                                    %>
                                    <li>
                                        <div class="dropdown">
                                            <a class="dropdown-toggle blacktemp" data-toggle="dropdown" href="#">
                                                ${selectedlanguage[1]}
                                                <b class="caret"></b>
                                            </a>
                                            <ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu">
                                                % for l in languages:
                                                    <li class="cursor">
                                                        <a href="#" onclick="updateQueryParams({'_LOCALE_': '${l[0]}'})">${l[1]}</a>
                                                    </li>
                                                % endfor
                                                </li>
                                            </ul>
                                        </div>
                                    </li>

                                    <li>|</li>
                                    <%
                                        from lmkp.views.translation import get_profiles
                                        profiles = get_profiles()
                                        selectedprofile = profiles[0]
                                        for p in profiles:
                                            if profile == p[0]:
                                                selectedprofile = p
                                    %>
                                    <li>
                                        <div class="dropdown">
                                            <a class="dropdown-toggle blacktemp" data-toggle="dropdown" href="#">
                                                ${selectedprofile[1]}
                                                <b class="caret"></b>
                                            </a>
                                            <ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu">
                                                % for p in profiles:
                                                    <li class="cursor">
                                                        <a href="#" onclick="updateQueryParams({'_PROFILE_': '${p[0]}'})">${p[1]}</a>
                                                    </li>
                                                % endfor
                                                </li>
                                            </ul>
                                        </div>
                                    </li>
                                </ul>
                            </div>
                    </div>
                </div>

                ## End of Header

                ## Show session messages if available
                % if request.session.peek_flash():
                    <div class="alert alert-block" style="margin-bottom:0;">
                        <button type="button" class="close" data-dismiss="alert">&times;</button>
                        % for message in request.session.pop_flash():
                            <p>
                                <% context.write(message) %>
                            </p>
                        % endfor
                    </div>
                % endif

                ## Content

                ## Use the body of the child template
                ${self.body()}

                ## End of Content

            </div>
            <div class="push"></div>
        </div>

        ## Footer

        <div class="navbar footer">
            <ul class="nav pull-right">
                <li>
                    <a href="#">
                        Faq
                    </a>
                </li>
                <li>|</li>
                <li>
                    <a href="#">
                        Imprint
                    </a>
                </li>
                <li>|</li>
                <li>
                    <a href="#">
                        Partners
                    </a>
                </li>
            </ul>
        </div>

        ## End of Footer

        <script type="text/javascript">
         /* <![CDATA[ */
         document.write(unescape("%3Cscript src='" + (("https:" == document.location.protocol) ? "https://" : "http://") + "www.google.com/jsapi' type='text/javascript'%3E%3C/script%3E"));
         /* ]]> */
        </script>

        <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
        <script>window.jQuery || document.write('<script src="${request.static_url("lmkp:static/media/js/vendor/jquery-1.9.1.min.js")}"><\/script>')</script>

        <script src="${request.static_url('lmkp:static/media/js/vendor/bootstrap.min.js')}"></script>

        <script src="${request.static_url('lmkp:static/media/js/main.js')}"></script>

        <script>
            var _gaq=[['_setAccount','UA-XXXXX-X'],['_trackPageview']];
            (function(d,t){var g=d.createElement(t),s=d.getElementsByTagName(t)[0];
            g.src=('https:'==location.protocol?'//ssl':'//www')+'.google-analytics.com/ga.js';
            s.parentNode.insertBefore(g,s)}(document,'script'));
        </script>
    
        ## Include the bottom tags of the child template if available.
        <%
            try:
                self.bottom_tags()
            except AttributeError:
                pass
        %>

    </body>

</html>
