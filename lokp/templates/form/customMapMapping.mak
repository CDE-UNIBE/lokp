<%
    from mako.template import Template
    from pyramid.path import AssetResolver
    from lokp.config.customization import get_customized_template_path
    import colander

    lmkpAssetResolver = AssetResolver('lokp')
    resolver = lmkpAssetResolver.resolve('templates/map/mapform.mak')
    template = Template(filename=resolver.abspath())
    activitiesResolver = lmkpAssetResolver.resolve(get_customized_template_path(request, 'parts/items/activities.mak'))
    activitiesTemplate = Template(filename=activitiesResolver.abspath())
    geometry = None if cstruct['geometry'] == colander.null else cstruct['geometry']
    _ = request.translate

    from lokp.views.filter import getFilterKeys
    from lokp.views.filter import getActiveFilters

    aFilterKeys, shFilterKeys = getFilterKeys(request)
    activeFilters = getActiveFilters(request)

    from mako.template import Template
    from mako.lookup import TemplateLookup

%>


## container containing map

<div id="${field.oid}" style="height: 400px;" class="map-div">
    ## Loading indicator

    <div class="preloader-wrapper big active map-loader" data-map-id="${field.oid}">
        <div class="spinner-layer spinner-teal-only">
            <div class="circle-clipper left">
                <div class="circle"></div>
            </div>
            <div class="gap-patch">
                <div class="circle"></div>
            </div>
            <div class="circle-clipper right">
                <div class="circle"></div>
            </div>
        </div>
    </div>
    ## Map buttons

    <div class="map-floating-buttons" id="map-floating-buttons-${field.oid}">
        <span class="range-field tooltipped" data-position="top" data-tooltip="${_('Transparency of context layers')}">
          <input type="range" class="layer-transparency-slider" min="0" max="100" value="60"
                 data-map-id="${field.oid}"/>
        </span>
        <a class="btn-floating tooltipped btn-large button-collapse" data-position="top"
           data-tooltip="${_('Map Options')}" data-activates="slide-out-map-options-${field.oid}">
            <i class="material-icons">map</i>
        </a>
        ##         <a class="btn-floating tooltipped btn-large button-collapse" data-position="top"
        ##            data-tooltip="${_('Add a Filter')}" data-activates="slide-out-filter-${field.oid}">
        ##             <i class="material-icons" style="margin-right: 15px;" data-position="top">filter_list</i>
        ##         </a>
        ##         % if len(activeFilters) == 1:
        ##             <span class="badge"
        ##                   style="color: white; background-color: #323232; position: relative; top: -25px; left: -40px; z-index: 1; border-radius: 5px;">${len(activeFilters)}
        ##                 active filter</span>
        ##         % else:
        ##             <span class="badge"
        ##                   style="color: white; background-color: #323232; position: relative; top: -25px; left: -40px; z-index: 1; border-radius: 5px;">${len(activeFilters)}
        ##                 active filters</span>
        ##         % endif
    </div>

    ## Manages green layer button

    <%doc>    <div class="map-form-controls">

            % if editmode == 'multipoints':
                <div class="form-map-edit pull-right">
                    <div class="btn-group pull-right" data-toggle="buttons-radio">
                        <a class="btn btn-mini active ttip" id="btn-add-point" data-toggle="tooltip"
                           title="${_('Add a location to the map')}"><i class="icon-plus"></i></a>
                        <a class="btn btn-mini ttip" id="btn-remove-point" data-toggle="tooltip"
                           title="${_('Remove a location from the map')}"><i class="icon-minus"></i></a>
                        <a class="btn btn-mini btn-danger disabled ttip disableClick"><i class="icon-pencil"></i></a>
                    </div>
                </div>
            % endif

            <div class="form-map-menu pull-right">
                <a class="btn-floating tooltipped btn-large button-collapse" style="margin-right: 15px; margin-top: 15px;"
                   data-position="top" data-tooltip="${_('Turn layers on and off')}" data-activates="slide-out-map-options">
                    <i class="material-icons">map</i>
                </a>
            </div>
        </div></%doc>
</div>





## file upload implemented accordint to https://developer.mozilla.org/en-US/docs/Web/API/File/Using_files_from_web_applications
% if field.title == "map11":
    <html>
    <head>
        <meta charset="UTF-8">
        <title>File(s) size</title>
        <script>
            function uploadShapefile() {
                var shpZip = document.getElementById("uploadInput").files[0];
                console.log('shpZip', shpZip);

                // send request to server

                function getBase64(file) {
                    var reader = new FileReader();
                    reader.readAsDataURL(file);
                    reader.onload = function () {
                        console.log(reader.result);
                    };
                    reader.onerror = function (error) {
                        console.log('Error: ', error);
                    };
                }

                $.ajax('/files/testupload', {
                    data: JSON.stringify({          // send uploaded file to server
                        shpZip: getBase64(shpZip)
                    })
                    ,
                    ## conversion to base64 in order to avoid 'TypeError: Illegal invocation'  -> try avoid automatic processing

                    type: "POST",
                    success: function (jsonResponse) {  // jsonResponse should contain coordinates
                        console.log(jsonResponse)
                    }
                });
                ## internal server error caused getBase64(shp_zip) --- must return a view!
                var nBytes = 0,
                        oFiles = document.getElementById("uploadInput").files,
                        nFiles = oFiles.length;
                for (var nFileId = 0; nFileId < nFiles; nFileId++) {
                    nBytes += oFiles[nFileId].size;
                }
                var sOutput = nBytes + " bytes";
                // optional code for multiples approximation
                for (var aMultiples = ["KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB"], nMultiple = 0, nApprox = nBytes / 1024; nApprox > 1; nApprox /= 1024, nMultiple++) {
                    sOutput = nApprox.toFixed(3) + " " + aMultiples[nMultiple] + " (" + nBytes + " bytes)";
                }
                // end of optional code
                document.getElementById("fileNum").innerHTML = nFiles;
                document.getElementById("fileSize").innerHTML = sOutput;
            }
        </script>
    </head>

    <body onload="uploadShapefile()">
    <form name="uploadForm">
        <p><input id="uploadInput" type="file" name="myFiles" onchange="uploadShapefile()" multiple> selected files:
            <span
                    id="fileNum">0</span>; total size: <span id="fileSize">0</span></p>
    </form>
    </body>
    </html>
% endif



## Map Menu

<div id="slide-out-map-options-${field.oid}" class="side-nav map-side-menu">

    ## Search

    <div class="row map-search-container">
        <div class="input-field col s11">
            <i class="material-icons prefix">search</i>
            <input id="js-map-search-${field.oid}" class="map-search-input" name="q" type="text">
        </div>
    </div>

    <ul class="collapsible" data-collapsible="accordion" data-map-id="${field.oid}">
        ## Deals

        <li>
            <div class="collapsible-header">
                <i class="material-icons">room</i>${_('Deals')}
            </div>
            <div class="collapsible-body">
                <form action="#" class="map-menu-form">
                    <input class="input-top js-activity-layer-toggle" type="checkbox"
                           id="activity-layer-toggle-${field.oid}" checked="checked">
                    <label class="text-primary-color" for="activity-layer-toggle-${field.oid}"
                           style="line-height: 22px; height: 22px;" id="map-deals-symbolization-${field.oid}">
                        ## Current symbolization (dropdown and legend)
            </label>
                    <ul id="map-points-list-${field.oid}" class="map-legend-points-symbols">
                        ## Points legend
            </ul>
                    <div id="map-polygons-list-${field.oid}">
                        ## Polygon list
            </div>
                </form>
            </div>
        </li>

        ## Base layers

        <li>
            <div class="collapsible-header">
                <i class="material-icons">map</i>${_('Base layers')}
            </div>
            <div class="collapsible-body">
                <form action="#" class="map-base-layer-entries">
                    <p>
                        <input class="with-gap js-base-map-layers" name="map-base-layers-${field.oid}" type="radio"
                               id="satelliteMapOption-${field.oid}" value="satelliteMap" checked="checked"/>
                        <label for="satelliteMapOption-${field.oid}">${_('Google Earth satellite images')}</label>
                    </p>
                    <p>
                        <input class="with-gap js-base-map-layers" name="map-base-layers-${field.oid}" type="radio"
                               id="esriSatelliteMapOption-${field.oid}" value="esriSatellite"/>
                        <label for="esriSatelliteMapOption-${field.oid}">${_('ESRI World Imagery')}</label>
                    </p>
                    <p>
                        <input class="with-gap js-base-map-layers" name="map-base-layers-${field.oid}" type="radio"
                               id="terrainMapOption-${field.oid}" value="terrainMap"/>
                        <label for="terrainMapOption-${field.oid}">${_('Google Terrain Map')}</label>
                    </p>
                    <p>
                        <input class="with-gap js-base-map-layers" name="map-base-layers-${field.oid}" type="radio"
                               id="streetMapOption-${field.oid}" value="streetMap"/>
                        <label for="streetMapOption-${field.oid}">${_('OpenStreetMap')}</label>
                    </p>
                </form>
            </div>
        </li>

        ## Context layers

        <li>
            <div class="collapsible-header">
                <i class="material-icons">layers</i>${_('Context layers')}
            </div>
            <div class="collapsible-body">
                <form action="#" id="context-layers-list-${field.oid}">
                    ## Context layers entries
          </form>
            </div>
        </li>
    </ul>
</div>

## Map modal (used for legend of context layers)

<div id="map-modal-${field.oid}" class="modal">
    <div id="map-modal-body-${field.oid}" class="modal-content">
        ## Placeholder for map modal
  </div>
    <div class="modal-footer">
        <a href="#" class="modal-action modal-close waves-effect waves-green btn-flat">${_('Close')}</a>
    </div>
</div>

## Filter (only once per page)

## <ul id="slide-out-filter-${field.oid}" class="side-nav map-side-menu">
##        <%include file="lokp:customization/omm/templates/parts/filter.mak" />
##</ul>



${template.render(request=request, geometry=geometry, editmode=editmode, _=_)}

% if field.errormsg:
    <li class="errorLi">
        <h3 class="errorMsgLbl">
            ${request.translate("There was a problem with this section")}
        </h3>
        <p class="errorMsg">
            ${request.translate(field.errormsg)}
        </p>
    </li>
% endif

% if field.description:
    <li class="section">
        <div>${field.description}</div>
    </li>
% endif

<div class="row" style="margin-top: 10px;">
    <div class="col s12">
        % if field.required:
            <span class="required-form-field"></span>
        % endif
        ${_('Set the location')}&nbsp;<span class="helpTooltip icon-question-sign tooltipped" data-position="top"
                                            data-delay="50"
                                            data-tooltip="${_('Use the toolbar to the right to draw the location. Please zoom in to set the geometry as accurately as possible.')}"></span>
        ##         <p style="margin-top: 10px;">${_('Please use the QGIS plugin to add or edit polygons.')} <a
        ##                 href="http://lokp.readthedocs.org/en/latest/qgis.html" target="_blank"
        ##                 class="text-accent-color">${_('Read more.')}</a></p>
    </div>
</div>

<script type="text/javascript">
    var tForSuccess = "${_('Success!')}";
    var tForInvalidFormat = "${_('Not in a valid format!')}";
</script>



## coordinates div appears when triggerCoordinatesDiv is clicked

<div id="coordinates-div" style="display: none;">
    <div class="row">
        <div class="col s8">
            <label for="map-coords-field">${_('Coordinates')}</label>
            <input id="map-coords-field" class="input-style" type="text"/>
        </div>
    </div>
    <div class="row">
        <div class="input-field col s8">
            <select id="map-coords-format">
                <option value="1">46&deg; 57.1578 N 7&deg; 26.1102 E</option>
                <option value="2">46&deg 57' 9.468" N 7&deg 26' 6.612" E</option>
                <option value="3">N 46&deg 57.1578 E 7&deg 26.1102</option>
                <option value="4">N 46&deg 57' 9.468" E 7&deg 26' 6.612"</option>
                <option value="5" selected>46.95263, 7.43517</option>
            </select>
            <label>Select Format</label>
        </div>
    </div>
    <div class="row">
        <div class="col s12">
            <button id="map-coords-button" class="btn btn-small"
                    onClick="javascript:return parseCoordinates('${field.oid}');">${_('Parse')}</button>
        </div>
        <div id="map-coords-message" class="col s8">
            <!-- Placeholder -->
        </div>
    </div>
</div>


${field.start_mapping()}

% for child in field.children:  ## renders childeren of form. Renders all fields defined in widget
        ${child.render_template(field.widget.item_template)}
% endfor

${field.end_mapping()}

<script>
    deform.addCallback(
            ['${field.oid}', '${field.title}'],
            function (args) {

                var oid = args[0];
                var title = args[1];

                console.log("foo", oid, title);

                if (window['loaded_maps'] === undefined) {
                    window['loaded_maps'] = [];
                }

                if (window['loaded_maps'].indexOf(title) === -1) {
                    createMap(oid, {pointsVisible: true, pointsCluster: true, geometry_type: ${geometry_type}}); // get geometry_type variable from python
                    window['loaded_maps'].push(title);
                } else {
                    $('#' + oid).hide();
                }
            }
    );
</script>
