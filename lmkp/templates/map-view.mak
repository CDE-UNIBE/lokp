<!DOCTYPE html>
<!--[if lt IE 7]>      <html class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]>         <html class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]>         <html class="no-js lt-ie9"> <![endif]-->
<!--[if gt IE 8]><!--> <html class="no-js"> <!--<![endif]-->
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
        <title>Land observatory</title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width">



        <link rel="stylesheet" href="/static/media/css/bootstrap-combined.no-icons.min.css">
        <link rel="stylesheet" href="/static/media/css/font-awesome/css/font-awesome.min.css">
        <link rel="stylesheet" href="/static/media/css/bootstrap-responsive.min.css">
        <link rel="stylesheet" href="/static/media/css/main.css">
        <link rel="stylesheet" href="/static/media/css/custom.css">

        <link rel="stylesheet" href="/static/lib/OpenLayers-2.12/theme/default/style.css" type="text/css">

        <style type="text/css" >
            .olTileImage {
                max-width: none !important;
            }
        </style>

        <script src="/static/lib/OpenLayers-2.12/OpenLayers.js" type="text/javascript"></script>

        <script type="text/javascript" src="http://maps.google.com/maps/api/js?v=3&amp;sensor=false"></script>

        <script src="/static/media/js/vendor/modernizr-2.6.2-respond-1.1.0.min.js" type="text/javascript"></script>
        <script src="/static/media/js/vendor/jquery-1.9.1.min.js" type="text/javascript"></script>
        <script src="/static/media/js/vendor/bootstrap.min.js" type="text/javascript"></script>
        <script src="/static/v2/jquery.cookie.js" type="text/javascript"></script>

        <script src="/static/v2/main.js" type="text/javascript"></script>

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
                            <a href="#">
                                <img src="/static/media/img/logo.png" />
                            </a>
                        </div>

                        <div class="top_menu">
                            <ul class="top-menu">
                                <li class="active grid"><a href="#"><i class="icon-map-marker"></i>&nbsp;&nbsp;Map</a></li>
                                <li><a href="#"><i class="icon-align-justify"></i>&nbsp;&nbsp;Grid</a></li>
                                <li><a href="#"><i class="icon-bar-chart"></i>&nbsp;&nbsp;Charts</a></li>
                            </ul>
                        </div>

                        <div class="user">
                            <ul class="nav nav-pills">
                                <li class="active"><a href="#">Login</a></li>
                                <li>|</li>
                                <li><a href="#">Englisch
                                        <span class="arrow"><i class="icon-sort-down"></i></span></a>
                                <li>|</li>
                                <li><a href="#">Profile
                                        <span class="arrow"><i class="icon-sort-down"></i></span></a>
                            </ul>
                        </div>


                    </div>
                </div>



                <!-- Filter-area  -->
                <form class="form-horizontal filter_area">
                    <div class="container">
                        <div class="control-group">
                            <label class="control-label">Active filters</label>
                            <div class="controls">
                                <input type="text" id="filter1" class="filter-variable1" placeholder="A sample variable > 23">
                                <span class="icon-remove1">
                                    <i class="icon-remove pointer"></i>
                                </span>
                            </div>
                        </div>
                        <div class="control-group">
                            <div class="controls">
                                <input type="text" id="filter2" class="filter-variable2" placeholder="Another sample variable = Combodia">
                                <span class="icon-remove2">
                                    <i class="icon-remove pointer"></i>
                                </span>
                            </div>
                        </div>
                        <div class="control-group new-filter new-filter">
                            <label class="control-label">New Filter</label>
                            <div class="controls">
                                <div class="btn-group">
                                    <button class="btn select_btn_filter">Tagggroup</button>
                                    <button class="btn select_btn_filter_right dropdown-toggle" data-toggle="dropdown">
                                        <span class="caret"></span>
                                    </button>
                                    <ul class="dropdown-menu">
                                        <li><a href="#">1</a></li>
                                        <li><a href="#">2</a></li>
                                        <li><a href="#">3</a></li>
                                        <li><a href="#">4</a></li>
                                        <li><a href="#">5</a></li>
                                    </ul>
                                </div>

                                <div class="btn-group">
                                    <button class="btn select_btn_operator">&#8804;</button>
                                    <button class="btn select_btn_operator_right dropdown-toggle" data-toggle="dropdown">
                                        <span class="caret"></span>
                                    </button>
                                    <ul class="dropdown-menu">
                                        <li><a href="#">&#8805;</a></li>
                                        <li><a href="#">=</a></li>
                                        <li><a href="#">!=</a></li>
                                    </ul>
                                </div>
                                <input type="text" class="filter-value" id="filter2" placeholder="Value">
                                <span class="icon-add">
                                    <i class="icon-plus pointer"></i>
                                </span>
                            </div>
                        </div>
                        <div class="favorite">
                            <div class="btn-group favorite">
                                <button class="btn btn_favorite">Favorite</button>
                                <button class="btn btn_favorite_right dropdown-toggle" data-toggle="dropdown">
                                    <span class="caret"></span>
                                </button>
                                <ul class="dropdown-menu">
                                    <li><a href="#">1</a></li>
                                    <li><a href="#">2</a></li>
                                    <li><a href="#">3</a></li>
                                    <li><a href="#">4</a></li>
                                    <li><a href="#">5</a></li>
                                </ul>
                            </div>
                        </div>
                    </div>


                </form>


                <div class="filter_area_openclose">
                    <i class="icon-double-angle-up pointer"></i>
                </div>



                <!-- content -->
                <div class="no-border">
                    <div class="map-whole-page shadow-inside">

                        <div id="map-div" style="width: 100%; height: 100%;"></div>

                    </div>
                    <div class="shadow-inside">
                    </div>
                </div>

                <div class="basic-data" style="z-index: 1000; display: none;">
                    <h6 class="deal-headline">Deal
                        <span id="deal-shortid-span" class="underline">#</span>
                    </h6>
                    <ul id="taggroups-ul">
                        <li>
                            <p>Select a deal to get information.</p>
                        </li>
                    </ul>
                </div>


                <!-- map menu -->
                <div class="map-menu" style="z-index: 1000;">
                    <form class="navbar-search" action="">
                        <input name="q" id="search" class="search-query" placeholder="search location">
                        <input type="submit" value="Search" id="search-submit">
                    </form><br>
                    <!-- Base layers -->
                    <div class="map-menu-base-layers">
                        <h6>Base layers</h6>

                        <ul>
                            <li>
                                <label class="radio inline">
                                    <input type="radio" class="baseMapOptions" name="baseMapOptions" id="streetMapOption" value="streetMap" checked>
                                    Street Map
                                </label>
                            </li>

                            <li>
                                <label class="radio inline">
                                    <input type="radio" class="baseMapOptions" name="baseMapOptions" id="satelliteMapOption" value="satelliteMap">
                                    Satellite Imagery
                                </label>
                            </li>

                            <li>
                                <label class="radio inline">
                                    <input type="radio" class="baseMapOptions" name="baseMapOptions" id="terrainMapOption" value="terrainMap">
                                    Terrain Map
                                </label>
                            </li>
                        </ul>

                    </div>



                    <hr class="lightgray">


                    <!-- Context layers -->
                    <div class="map-menu-context-layers">

                        <h6>Context layers</h6>

                        <ul>

                            <li>
                                <div class="checkbox-modified-small">
                                    <input class="input-top" type="checkbox" value="Accessibility" id="checkboxAccessibility">
                                    <label for="checkboxAccessibility"></label>
                                </div>
                                <p class="context-layers-description">
                                    Accessibility&nbsp;
                                    <i class="icon-exclamation-sign pointer"></i>
                                </p>       
                            </li>

                            <li>
                                <div class="checkbox-modified-small">
                                    <input class="input-top" type="checkbox" value="PopulationDensity2008" id="checkboxPopulationDensity2008">
                                    <label for="checkboxPopulationDensity2008"></label>
                                </div>
                                <p class="context-layers-description">
                                    Population Density 2008&nbsp;
                                    <i class="icon-exclamation-sign pointer"></i>
                                </p>  
                            </li>

                            <li>
                                <div class="checkbox-modified-small">
                                    <input class="input-top" type="checkbox" value="GlobalLandCover2009" id="checkboxGlobalLandCover2009">
                                    <label for="checkboxGlobalLandCover2009"></label>
                                </div>
                                <p class="context-layers-description">
                                    Global LandCover 2009&nbsp;
                                    <i class="icon-exclamation-sign pointer"></i>
                                </p>         
                            </li>

                            <li>
                                <div class="checkbox-modified-small">
                                    <input class="input-top" type="checkbox" value="GlobalCropland" id="checkboxGlobalCropland">
                                    <label for="checkboxGlobalCropland"></label>
                                </div>
                                <p class="context-layers-description">
                                    Global Cropland&nbsp;
                                    <i class="icon-exclamation-sign pointer"></i>
                                </p>
                            </li>

                            <li>
                                <div class="checkbox-modified-small">
                                    <input class="input-top" type="checkbox" value="GlobalPastureLand" id="checkboxGlobalPastureLand">
                                    <label for="checkboxGlobalPastureLand"></label>
                                </div>
                                <p class="context-layers-description">
                                    Global Pasture Land&nbsp;
                                    <i class="icon-exclamation-sign pointer"></i>
                                </p>
                            </li>
                        </ul>

                    </div>


                </div>

            </div>

            <div class="push"></div>
        </div>

        <div class="navbar footer footer-map">

            <ul class="nav pull-right">
                <li><a href="#">Faq</a></li>
                <li>|</li>
                <li><a href="#">Imprint</a></li>
                <li>|</li>
                <li><a href="#">Partners</a></li>
            </ul>

        </div>

    </body>
</html>

