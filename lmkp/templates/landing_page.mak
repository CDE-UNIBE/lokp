<%
from lmkp.views.views import getQueryString
from lmkp.views.translation import get_profiles
from lmkp.views.translation import get_languages
profiles = sorted(get_profiles(), key=lambda profile: profile[0])
languages = get_languages()
selectedlanguage = languages[0]
for l in languages:
    if locale == l[0]:
        selectedlanguage = l
mode = None
if 'lmkp.mode' in request.registry.settings:
    if str(request.registry.settings['lmkp.mode']).lower() == 'demo':
        mode = 'demo'
%>

<!DOCTYPE html>
<!--[if lt IE 7]>      <html class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]>         <html class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]>         <html class="no-js lt-ie9"> <![endif]-->
<!--[if gt IE 8]><!--> <html class="no-js"> <!--<![endif]-->
    <head>
        <meta charset="utf-8">
        <meta name="content-language" content="${selectedlanguage[0]}" />
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <title>Land Observatory</title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width">

        <link rel="stylesheet" href="${request.static_url('lmkp:static/media/css/bootstrap-combined.no-icons.min.css')}">
        <link rel="stylesheet" href="${request.static_url('lmkp:static/media/css/font-awesome/css/font-awesome.min.css')}">

        <link rel="stylesheet" href="${request.static_url('lmkp:static/media/css/bootstrap-responsive.min.css')}">
        <link rel="stylesheet" href="${request.static_url('lmkp:static/media/css/main.css')}">

        <link rel="stylesheet" href="${request.static_url('lmkp:static/media/css/custom.css')}">

        <!--[if IE 7]>

            <link rel="stylesheet" href="${request.static_url('lmkp:static/media/css/ie7.css')}">
            <link rel="stylesheet" href="${request.static_url('lmkp:static/media/css/font-awesome/css/font-awesome-ie7.css')}">

        <![endif]-->

        <!--[if IE 8]>

            <link rel="stylesheet" href="${request.static_url('lmkp:static/media/css/ie8.css')}">

        <![endif]-->

        <script src="${request.static_url('lmkp:static/media/js/vendor/modernizr-2.6.2-respond-1.1.0.min.js')}"></script>
        <script src="${request.static_url('lmkp:static/media/js/vendor/jquery-1.9.1.min.js')}"></script>

        <style type="text/css">
            .user {
                margin-top: -8px;
                padding-right: 0;
            }
            #main {
                padding-bottom: 50px;
            }
            .wrap {
                margin: 0 auto -50px;
            }
            .header_self {
                height: inherit;
                max-height: none;
            }
            .lo_logo {
                margin: 0 0 5px 5px;
            }
            .btn-country-selector {
                text-transform: uppercase;
            }
        </style>

        <script type="text/javascript">

            jQuery(document).bind('keyup', function(e) {

                if(e.keyCode==39){
                    jQuery('a.carousel-control.right').trigger('click');
                }

                else if(e.keyCode==37){
                    jQuery('a.carousel-control.left').trigger('click');
                }

            });

        </script>

    </head>
    <body>
        <!--[if lt IE 7]>
            <p class="chromeframe">You are using an <strong>outdated</strong> browser. Please <a href="http://browsehappy.com/">upgrade your browser</a> or <a href="http://www.google.com/chromeframe/?redirect=true">activate Google Chrome Frame</a> to improve your experience.</p>
        <![endif]-->

	    <div class="wrap">

	    <!-- Header  -->

                <div id="main" class="clearfix">

                    <div class="navbar header_self">
                        <div class="container">
                            <div class="row-fluid hidden-phone">
                                <div class="span3 text-right">
                                    <a href="${request.route_url('index')}">
                                        <img src="${request.static_url('lmkp:static/media/img/logo.png')}" class="lo_logo" />
                                    </a>
                                </div>

                                <div class="span6 landing-introduction">
                                    <p>
                                        The <b>Land Observatory</b> is a pilot project by some partners of the <a href="http://www.landmatrix.org">Land Matrix</a>, designed to provide greater context and deeper insight on land deals, from a more local perspective.
                                    </p>
                                </div>
                                <div class="user">
                                    <ul class="nav nav-pills">
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
                                    </ul>
                                </div>
                            </div>
                            <div class="row-fluid visible-phone">
                                <div class="span3">
                                    <a href="${request.route_url('index')}">
                                        <img src="${request.static_url('lmkp:static/media/img/logo.png')}" class="lo_logo" />
                                    </a>
                                </div>
                                <div class="span6 landing-introduction">
                                    <p>
                                        The <b>Land Observatory</b> is a pilot project by some partners of the <a href="http://www.landmatrix.org">Land Matrix</a>, designed to provide greater context and deeper insight on land deals, from a more local perspective.
                                    </p>
                                </div>
                                <div class="span3">
                                    <div class="user">
                                        <ul class="nav nav-pills">
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
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- content -->

                    <div class="container">
                        <div class="content no-border">

    <!--                        <div class="row-fluid">
                                <div class="span offset1">
                                    To start,  please
                                </div>
                            </div>-->

                            <div class="row-fluid action">
                                <div class="span2 offset1">
                                    Select a country
                                </div>
                                <div class="span3">
                                    <div class="country-selector">
                                       <div class="btn-group">
                                           <button class="btn btn-country-selector">${profiles[0][1]}</button>
                                           <button class="btn btn_favorite_right dropdown-toggle" data-toggle="dropdown">
                                               <i class="icon-caret-down"></i>
                                           </button>
                                           <ul class="dropdown-menu country-selector">
                                               % for p in profiles:
                                                <li><a href="/${p[1]}">${p[0]}</a></li>
                                                % endfor
                                           </ul>
                                       </div>
                                    </div>
                                </div>
                            </div>

                            <div class="row-fluid not-action">
                                <div class="span offset1">
                                    Or take a short tour:
                                </div>
                            </div>

                            <div class="row-fluid">
                                <div class="span10 offset1">

                                    <!-- slider -->
                                    <div id="myCarousel" class="carousel slide">
                                        <ol class="carousel-indicators">
                                            <li data-target="#myCarousel" data-slide-to="0" class="active"></li>
                                            <li data-target="#myCarousel" data-slide-to="1"></li>
                                            <li data-target="#myCarousel" data-slide-to="2"></li>
                                            <li data-target="#myCarousel" data-slide-to="3"></li>
                                            <li data-target="#myCarousel" data-slide-to="4"></li>
                                            <li data-target="#myCarousel" data-slide-to="5"></li>
                                            <li data-target="#myCarousel" data-slide-to="6"></li>
                                        </ol>

                                        <!-- Carousel items -->
                                        <div class="carousel-inner">


                                            <div class="item active">
<!--                                                <div class="not-action2">
                                                    Or take a short tour.
                                                </div>-->
                                                <img class="slide" src="${request.static_url('lmkp:static/media/img/slides/slider-image_02.png')}" alt="">
                                                <div class="carousel-caption">
                                                    <h4>Second Thumbnail label</h4>
                                                    <p>Users in select pilot countries gather, explore and analyze spatial data on large-scale land acquisitions.
                                                    Data is managed and reviewed locally by partners.
                                                    </p>
                                                </div>
                                            </div>

                                            <div class="item">
                                                <img class="slide" src="${request.static_url('lmkp:static/media/img/slides/slider-image_03.png')}" alt="">
                                                <div class="carousel-caption">
                                                    <h4>Third Thumbnail label</h4>
                                                    <p>Users can see deals in full geographical context, learn more about investors and the kinds of investments in question.</p>
                                                </div>
                                            </div>

                                            <div class="item">
                                                <img class="slide" src="${request.static_url('lmkp:static/media/img/slides/slider-image_04.png')}" alt="">
                                                <div class="carousel-caption">
                                                    <h4>Third Thumbnail label</h4>
                                                    <p>You can also select a specific land deal to see more: "who" (investors and other stakeholders) and "what" the land will be used for </p>
                                                </div>
                                            </div>

                                            <div class="item">
                                                <img class="slide" src="${request.static_url('lmkp:static/media/img/slides/slider-image_05.png')}" alt="">
                                                <div class="carousel-caption">
                                                    <h4>Fifth Thumbnail label</h4>
                                                    <p>You can go further and learn more about an investor, seeing the same investor's other land deals.</p>
                                                </div>
                                            </div>

                                            <div class="item">
                                                <img class="slide" src="${request.static_url('lmkp:static/media/img/slides/slider-image_06.png')}" alt="">
                                                <div class="carousel-caption">
                                                    <h4>Sixth Thumbnail label</h4>
                                                    <p>Logged in users can also help contribute and update data, and anybody can freely comment on it. </p>
                                                </div>
                                            </div>

                                            <div class="item">
                                                <img class="slide" src="${request.static_url('lmkp:static/media/img/slides/slider-image_07.png')}" alt="">
                                                <div class="carousel-caption">
                                                    <h4>Sixth Thumbnail label</h4>
                                                    <p>You can filter the land deals by various attributes - like size, or crop. Or make a spatial selection of land deals</p>
                                                </div>
                                            </div>

                                            <div class="item">
                                                <img class="slide" src="${request.static_url('lmkp:static/media/img/slides/slider-image_08.png')}" alt="">
                                                <div class="carousel-caption">
                                                    <h4>Seventh Thumbnail label</h4>
                                                    <p>Want to know if anybody lives on a concession? Use the context layers to view population density and more</p>
                                                </div>
                                            </div>

                                        </div>

                                        <!-- Carousel nav -->
                                        <div class="carousel-controls">
                                                <a class="carousel-control left" href="#myCarousel" data-slide="prev">&lsaquo;</a>
                                                <a class="carousel-control right" href="#myCarousel" data-slide="next">&rsaquo;</a>
                                        </div>

                                    </div>
                                </div>

                            </div>
                        </div>
                    </div>
                </div>

                <div class="landing-page-push">
                </div>

            </div>

            <div class="navbar footer landing-page-footer">
                <ul class="nav pull-right">
                    <%
                        # The entries of the footer as arrays with
                        # - url
                        # - name
                        footer = [
                            [request.route_url('faq_view'), 'FAQ'],
                            [request.route_url('about_view'), 'About'],
                            [request.route_url('partners_view'), 'Partners & Donors']
                        ]
                    %>

                    % for f in footer:
                    <li
                        % if request.current_route_url() == f[0]:
                            class="active"
                        % endif
                        >
                        <a href="${f[0]}">${f[1]}</a>
                    </li>
                    % endfor
                </ul>
            </div>

        <script type="text/javascript">
         /* <![CDATA[ */
         document.write(unescape("%3Cscript src='" + (("https:" == document.location.protocol) ? "https://" : "http://") + "www.google.com/jsapi' type='text/javascript'%3E%3C/script%3E"));
         /* ]]> */
        </script>

        <script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
        <script>window.jQuery || document.write('<script src="${request.static_url("lmkp:static/media/js/vendor/jquery-1.9.1.min.js")}"><\/script>')</script>

        <script src="${request.static_url('lmkp:static/media/js/vendor/bootstrap.min.js')}"></script>

        <script src="${request.static_url('lmkp:static/media/js/main.js')}"></script>

        <script type="text/javascript">
          var _gaq = _gaq || [];
          _gaq.push(['_setAccount', 'UA-42520999-1']);
          _gaq.push(['_trackPageview']);

          (function() {
            var ga = document.createElement('script'); ga.type = 'text/javascript'; ga.async = true;
            ga.src = ('https:' == document.location.protocol ? 'https://ssl' : 'http://www') + '.google-analytics.com/ga.js';
            var s = document.getElementsByTagName('script')[0]; s.parentNode.insertBefore(ga, s);
          })();
        </script>
    </body>
</html>