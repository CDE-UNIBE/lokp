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

    allow_shapefile_upload = geometry_type['geometry_type'] == 'polygon'

    # This is a temporary solution: Allow multiple features for polygons, not for points.
    draw_multiple_features = 'true' if allow_shapefile_upload else 'false'
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

<div id="map-modal-${field.oid}" class="modal map-modal">
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

<div class="row map-actions">
  <div class="col s12">
    <ul class="tabs tabs-fixed-width z-depth-1">
      <li class="tab"><a href="#tab-${field.oid}-1">${_('Instructions')}</a></li>
      <li class="tab"><a href="#tab-${field.oid}-2">${_('Parse coordinates')}</a></li>
      <li class="tab${' disabled' if not allow_shapefile_upload else ''}"><a href="#tab-${field.oid}-3">${_('Upload shapefile')}</a></li>
    </ul>
  </div>
  <div id="tab-${field.oid}-1" class="col s12">
    <div class="tab-content-bordered">
      % if geometry_type['geometry_type'] == 'point':
        <p>${_('Set the location of the deal.')}</p>
      % else:
        <p>${_('Set the corresponding area.')}</p>
      % endif
      <p>${_('Use the toolbar to the right to draw the location. Please zoom in to set the geometry as accurately as possible.')}</p>
    </div>
  </div>
  <div id="tab-${field.oid}-2" class="col s12">
    <div class="tab-content-bordered">
      <div class="row">
        <div class="col s12">
          <p>You can enter coordinates to zoom to a certain location. Please note that you will still have to set a point or draw a polygon manually.</p>
          <br>
        </div>
        <div class="col s8">
          <label for="map-coords-field-${field.oid}">${_('Coordinates')}</label>
          <input id="map-coords-field-${field.oid}" class="input-style" type="text"/>
        </div>
      </div>
      <div class="row">
        <div class="input-field col s8">
          <select id="map-coords-format-${field.oid}">
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
                  onClick="javascript:parseCoordinates('${field.oid}'); return false;">${_('Parse')}</button>
        </div>
      </div>
    </div>
  </div>
  <div id="tab-${field.oid}-3" class="col s12">
    <div class="tab-content-bordered">
      % if allow_shapefile_upload:
        <div class="row map-shapefile-dropzone">
          <div class="col s12">
            <p>You can upload the necessary parts of a Shapfile (.shp, .dbf, .shx) either as separate files or as a .zip file. The files will be deleted from the server directly after the upload.</p>
            <p>Caution: Uploading a Shapefile will remove all previous geometries from the map!</p>
            <form action="${request.route_url('shp_upload')}" class="dropzone" id="dropzone-${field.oid}">
              <div class="fallback">
                <input name="file" type="file" multiple />
              </div>
            </form>
            <button class="btn btn-small btn-primary" onclick="Dropzone.forElement('#dropzone-${field.oid}').processQueue(); return false;">Upload</button>
            <button class="btn btn-small btn-warning right" onclick="Dropzone.forElement('#dropzone-${field.oid}').removeAllFiles(true); return false;">Remove all</button>
          </div>
        </div>
      % endif
    </div>
  </div>
  <div class="col s12 map-actions-feedback">
    <div class="alert alert-success closable-alert" id="map-actions-feedback-${field.oid}" style="display: none;">
      <div class="js-error-message"><!-- Placeholder --></div>
      <i class="material-icons alert-close-icon js-alert-hide">close</i>
    </div>
  </div>
</div>

<script type="text/javascript">
    var tForSuccess = "${_('Success!')}";
    var tForInvalidFormat = "${_('Not in a valid format!')}";
</script>

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

                if (window['loaded_maps'] === undefined) {
                    window['loaded_maps'] = [];
                }

                if (window['loaded_maps'].indexOf(title) === -1) {
                    createMap(oid, {pointsVisible: true, pointsCluster: true, geometry_type: ${geometry_type}, draw_multiple_features: ${draw_multiple_features}, label: '${label}'});
                    window['loaded_maps'].push(title);
                } else {
                    $('#' + oid).hide();
                }
            }
    );
    
    % if allow_shapefile_upload:
       $('#dropzone-${field.oid}').dropzone({
         uploadMultiple: true,
         autoProcessQueue: false,
         addRemoveLinks: true,
         parallelUploads: 10,
         init: function() {
             this.on('successmultiple', function(files, response) {
                 var mapOptions = getMapOptionsById('${field.oid}');
                 
                 // Get the new drawn features based on the response.
                 var newDrawnFeatures = getDrawnFeatures(response, mapOptions.options.label);

                 // Remove all existing drawn features.
                 mapOptions.drawnFeatures.eachLayer(function(layer) {
                     mapOptions.drawnFeatures.removeLayer(layer);
                 });

                 // Add the new drawn features and zoom to them.
                 newDrawnFeatures.eachLayer(function(layer) {
                     mapOptions.drawnFeatures.addLayer(layer);
                 });
                 mapOptions.map.fitBounds(newDrawnFeatures.getBounds());

                 // Update the geometry field.
                 updateGeometryField(mapOptions.map, newDrawnFeatures);

                 // Reset the upload field
                 this.removeAllFiles();

                 showParseFeedback('${field.oid}', 'Shapefile successfully uploaded.', 'success');
             })
                 .on('error', function(file, response) {
                     showParseFeedback('${field.oid}', response.error, 'error');
                 });
         }
       });
    % endif
</script>
