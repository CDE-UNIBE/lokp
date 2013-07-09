<%
from lmkp.views.views import getQueryString
from lmkp.views.translation import get_languages
from lmkp.views.translation import get_profiles
languages = get_languages()
selectedlanguage = languages[0]
for l in languages:
    if locale == l[0]:
        selectedlanguage = l
profiles = get_profiles()
selectedprofile = None
for p in profiles:
    if profile == p[0]:
        selectedprofile = p
%>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<!--[if lt IE 7]>      <html xmlns="http://www.w3.org/1999/xhtml" class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]>         <html xmlns="http://www.w3.org/1999/xhtml" class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]>         <html xmlns="http://www.w3.org/1999/xhtml" class="no-js lt-ie9"> <![endif]-->
<!--[if gt IE 8]><!--> <html xmlns="http://www.w3.org/1999/xhtml" class="no-js"> <!--<![endif]-->
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <meta name="content-language" content="${selectedlanguage[0]}" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
        <link rel="icon" type="image/ico" href="/favicon.ico"/>
        <title>
            <%
                try:
                    self.title()
                except AttributeError:
                    context.write("Land Observatory")
            %>
        </title>
        <meta name="description" content="" />
        <meta name="viewport" content="width=device-width" />

        <link rel="stylesheet" href="${request.static_url('lmkp:static/media/css/bootstrap-combined.no-icons.min.css')}" ></link>
        <link rel="stylesheet" href="${request.static_url('lmkp:static/media/css/font-awesome/css/font-awesome.min.css')}" ></link>

        <link rel="stylesheet" href="${request.static_url('lmkp:static/media/css/bootstrap-responsive.min.css')}"></link>
        <link rel="stylesheet" href="${request.static_url('lmkp:static/media/css/main.css')}"></link>

        <link rel="stylesheet" href="${request.static_url('lmkp:static/media/css/custom.css')}"></link>

        <!--[if IE 7]>

            <link rel="stylesheet" href="${request.static_url('lmkp:static/media/css/ie7.css')}"></link>
            <link rel="stylesheet" href="${request.static_url('lmkp:static/media/css/font-awesome/css/font-awesome-ie7.css')}"></link>

        <![endif]-->


        <!--[if IE 8]>

            <link rel="stylesheet" href="../media/css/ie8.css"></link>

        <![endif]-->

        <script type="text/javascript" src="${request.static_url('lmkp:static/media/js/vendor/modernizr-2.6.2-respond-1.1.0.min.js')}"></script>

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
            .desired-form-field:after {
                content: '*';
                font-weight: bold;
                color: #3a87ad;
            }
            .required-form-field:after {
                content: '*';
                font-weight: bold;
                color: #b94a48;
            }
            .sequencestyle {
                background-color: #F7F7F7;
                border: 1px solid silver;
                color: #333333;
            }
            .sequence-close {
                color: #8B1A1A;
                opacity: 0.5;
            }
            .filter_area_openclose {
                cursor: pointer;
            }
            #new-filter-value {
                width: 178px;
            }
            .input-append #new-filter-value {
                width: 147px;
            }
            .new-filter .dropdown-menu {
                max-height: 300px;
                overflow-y: auto;
                overflow-x: hidden;
            }
            #new-filter-value-box button {
                margin-right: 0;
            }
            .select_btn_operator_right {
                margin-right: 3px;
            }
            .filterCategory {
                font-weight: bold;
                padding: 5px 0 5px 10px;
            }
            #new-filter-key {
                overflow: hidden;
                width: 108px;
            }
            #new-filter-operator-display {
                width: 40px;
                overflow: hidden;
            }
            .filter_area input:focus {
                border: medium none;
                box-shadow: none;
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
                                        # - an array of urls (the first one being used for the link)
                                        # - icon (li class)
                                        # - name
                                        topmenu = [
                                            [
                                                [request.route_url('map_view')],
                                                'icon-map-marker',
                                                'Map'
                                            ], [
                                                [
                                                    request.route_url('grid_view'),
                                                    request.route_url('activities_read_many', output='html'),
                                                    request.route_url('stakeholders_read_many', output='html')
                                                ],
                                                'icon-align-justify',
                                                'Grid'
                                            ], [
                                                [request.route_url('charts_view')],
                                                'icon-bar-chart',
                                                'Charts'
                                            ]
                                        ]
                                    %>

                                    % for t in topmenu:
                                        <li
                                            % if request.current_route_url() in t[0]:
                                                class="active grid"
                                            % endif
                                            >
                                            <a href="${t[0][0]}">
                                                <i class="${t[1]}"></i>&nbsp;&nbsp;${t[2]}
                                            </a>
                                        </li>
                                    % endfor

                                    ## If the user is logged in, show link to add a new deal
                                    % if request.user:
                                        <li></li>
                                        <li
                                            % if request.current_route_url() == request.route_url('activities_read_many', output='form'):
                                                class="active grid"
                                            % endif
                                            >
                                            <a href="${request.route_url('activities_read_many', output='form')}" >
                                                <i class="icon-pencil"></i>
                                                New Deal
                                            </a>
                                        </li>
                                    % endif
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
                                        <li>/</li>
                                        <li class="active">
                                            <div>
                                                <a class="blacktemp" href="${request.route_url('user_self_registration')}">
                                                    Register
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
                                    <li>
                                        <div class="dropdown">
                                            <a class="dropdown-toggle blacktemp" data-toggle="dropdown" href="#">
                                                ${selectedlanguage[1]}
                                                <b class="caret"></b>
                                            </a>
                                            <ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu">
                                                % for l in languages:
                                                    <li class="cursor">
                                                        <a href="${getQueryString(request.url, add=[('_LOCALE_', l[0])])}">${l[1]}</a>
                                                    </li>
                                                % endfor
                                            </ul>
                                        </div>
                                    </li>
                                    % if len(profiles) >= 1:
                                        <li>|</li>
                                        <li>
                                            <div class="dropdown">
                                                <a class="dropdown-toggle blacktemp" data-toggle="dropdown" href="#">
                                                    % if selectedprofile is None:
                                                        Select Profile
                                                    % else:
                                                        ${selectedprofile[1]}
                                                    % endif
                                                    <b class="caret"></b>
                                                </a>
                                                <ul class="dropdown-menu" role="menu" aria-labelledby="dropdownMenu">
                                                    % for p in profiles:
                                                        <li class="cursor">
                                                            <a href="${getQueryString(request.url, add=[('_PROFILE_', p[0])])}">${p[1]}</a>
                                                        </li>
                                                    % endfor
                                                </ul>
                                            </div>
                                        </li>
                                    % endif
                                </ul>
                            </div>
                    </div>
                </div>

                ## End of Header

                ## Show session messages if available
                % if request.session.peek_flash():
                <div class="row-fluid">
                    <div class="alert alert-block" style="margin-bottom:0;">
                        % for message in request.session.pop_flash():
                            <p>
                                <% context.write(message) %>
                            </p>
                        % endfor
                    </div>
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

                <%
                # The entries of the footer as arrays with
                # - url
                # - name
                footer = [
                    ['#', 'FAQ'],
                    ['#', 'About'],
                    ['#', 'Partners'],
                    ['#', 'Blog']
                ]
                %>

                % for f in footer:
                    <li>
                        <a href="${f[0]}">${f[1]}</a>
                    </li>
                % endfor
            </ul>
        </div>

        ## End of Footer

        <script type="text/javascript">
         /* <![CDATA[ */
         document.write(unescape("%3Cscript src='" + (("https:" == document.location.protocol) ? "https://" : "http://") + "www.google.com/jsapi' type='text/javascript'%3E%3C/script%3E"));
         /* ]]> */
        </script>

        <script type="text/javascript" src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
        <script>window.jQuery || document.write('<script type="text/javascript" src="${request.static_url("lmkp:static/media/js/vendor/jquery-1.9.1.min.js")}"><\/script>')</script>

        <script type="text/javascript" src="${request.static_url('lmkp:static/media/js/vendor/bootstrap.min.js')}"></script>

        <script type="text/javascript" src="${request.static_url('lmkp:static/v2/main.js')}"></script>

        <script type="text/javascript">
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
