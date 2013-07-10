<%
from lmkp.views.translation import get_profiles
profiles = get_profiles()
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

            #main {
                padding-bottom: 50px;
            }

            .wrap {
                margin: 0 auto -50px;
            }

            ul.country-selector {
                text-transform: uppercase;
            }

            /* Tin's edits */

            .landing-action {

            }
            .landing-action p {
                float: left;
                margin: 5px;
            }
            .logo {
                float: left;
            }

            .carousel-caption p {
                font-size: 16px;
            }
            .carousel-caption {
                opacity: 0.8;
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
	                <div class="logo">
                            <a href="${request.route_url('index')}">
                                <img src="${request.static_url('lmkp:static/media/img/logo.png')}" />
	                    </a>
	                </div>

	            	<div class="span6 landing-action">
                            <p>
                            The <b>Land Observatory</b> is a pilot project by some partners of the <a href="http://www.landmatrix.org">Land Matrix</a>, designed to provide greater context and deeper insight on land deals, from a more local perspective. Please <b>choose a country</b> from the drop-down menu:
                            </p>
                        </div>
                        <div class="span2">
                            <div class="country-selector">
                                <div class="btn-group">
                                    <button class="btn btn-country-selector">Select country</button>
                                    <button class="btn btn_favorite_right dropdown-toggle" data-toggle="dropdown">
                                        <span class="caret"></span>
                                    </button>
                                    <ul class="dropdown-menu country-selector">
                                        % for p in sorted(profiles, key=lambda profile: profile[0]):
                                            <li><a href="/${p[0]}">${p[0]}</a></li>
                                        % endfor
                                    </ul>
                                </div>
                            </div>
                        </div>
	            </div>
	        </div>

	    	<!-- content -->

	        <div class="container">
	            <div class="content no-border">
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

        <script>
            var _gaq=[['_setAccount','UA-XXXXX-X'],['_trackPageview']];
            (function(d,t){var g=d.createElement(t),s=d.getElementsByTagName(t)[0];
            g.src=('https:'==location.protocol?'//ssl':'//www')+'.google-analytics.com/ga.js';
            s.parentNode.insertBefore(g,s)}(document,'script'));
        </script>
    </body>
</html>