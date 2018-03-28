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



% if field.title:   ## Field stands for for deform.field which refers a schema node, such as mapWidget

    <legend>${field.title}</legend>
% endif
## container containing map

<div id="${field.title}" style="height: 400px;"> ## variable title is passed by config/form.py/getMapWidget
    ## Loading indicator

    <div class="preloader-wrapper big active map-loader" data-map-id="${field.title}">
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

    <div class="map-floating-buttons" id="map-floating-buttons-${field.title}">
        <span class="range-field tooltipped" data-position="top" data-tooltip="${_('Transparency of context layers')}">
          <input type="range" class="layer-transparency-slider" min="0" max="100" value="60"
                 data-map-id="${field.title}"/>
        </span>
        <a class="btn-floating tooltipped btn-large button-collapse" data-position="top"
           data-tooltip="${_('Map Options')}" data-activates="slide-out-map-options-${field.title}">
            <i class="material-icons">map</i>
        </a>
        <a class="btn-floating tooltipped btn-large button-collapse" data-position="top"
           data-tooltip="${_('Add a Filter')}" data-activates="slide-out-filter-${field.title}">
            <i class="material-icons" style="margin-right: 15px;" data-position="top">filter_list</i>
        </a>
        % if len(activeFilters) == 1:
            <span class="badge"
                  style="color: white; background-color: #323232; position: relative; top: -25px; left: -40px; z-index: 1; border-radius: 5px;">${len(activeFilters)}
                active filter</span>
        % else:
            <span class="badge"
                  style="color: white; background-color: #323232; position: relative; top: -25px; left: -40px; z-index: 1; border-radius: 5px;">${len(activeFilters)}
                active filters</span>
        % endif
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

##----------------------------
## Shapefile upload


<a id="test-shapefile-uploader-${field.title}" class="modal-trigger waves-effect waves-light btn" href="#formModal"
   onclick="return uploadFile(event, this);" style="margin-bottom: 15px;">${_('Upload a file')}</a>

## duplicated from customFileDisplay.mak
<script>
    function uploadFile(event, btn) {
        event.preventDefault();

        // Set a loading indicator and show the modal window.
        $('#formModal').modal({
            backdrop: 'static'
        });

        // Remove old indicator and add a new one. This is used to know for
        // which field we are currently uploading a File.
        $('span#currentlyuploadingfile').remove();
        var tagContainer = $(btn).parent('div');
        tagContainer.append('<span id="currentlyuploadingfile"></span>');

        // Query and set the content of the modal window.
        $.ajax({
            url: '${request.route_url("file_upload_form_embedded")}'  // rout calls fileupload_embedded.mak
        }).done(function (data) {
            $('#formModal .modal-content').html(data);
            deform.load();
            if (!$('#formModal').hasClass('open')) {
                // Open modal
                $('#formModal').openModal();
            }
        });

        // Do not submit anything.
        return false;
    }

    /**
     * Function to add a newly uploaded file to the list.
     * Adds the values to the internal file information and triggers an update
     * of the visible list with filenames.
     */
    function addUploadedFile(filename, identifier) {

        // Get the textfield with file informations based on the indicator set.
        var hiddenField = $('#currentlyuploadingfile')
            .parent('div')
            .find('input.fileinformations');

        // Add and set the new values.
        var oldValue = hiddenField.val();
        var newValue = filename + '|' + identifier;
        if (oldValue != '') {
            newValue = [oldValue, newValue].join(',');
        }
        hiddenField.val(newValue);

        // Call function to do an update of the list with filenames.

        //updateExistingFiles(hiddenField);
    }

</script>







## Map Menu

<div id="slide-out-map-options-${field.title}" class="side-nav map-side-menu">

    ## Search

    <div class="row map-search-container">
        <div class="input-field col s11">
            <i class="material-icons prefix">search</i>
            <input id="js-map-search-${field.title}" class="map-search-input" name="q" type="text">
        </div>
    </div>

    <ul class="collapsible" data-collapsible="accordion" data-map-id="${field.title}">
        ## Deals

        <li>
            <div class="collapsible-header">
                <i class="material-icons">room</i>${_('Deals')}
            </div>
            <div class="collapsible-body">
                <form action="#" class="map-menu-form">
                    <input class="input-top js-activity-layer-toggle" type="checkbox"
                           id="activity-layer-toggle-${field.title}" checked="checked">
                    <label class="text-primary-color" for="activity-layer-toggle-${field.title}"
                           style="line-height: 22px; height: 22px;" id="map-deals-symbolization-${field.title}">
                        ## Current symbolization (dropdown and legend)
            </label>
                    <ul id="map-points-list-${field.title}" class="map-legend-points-symbols">
                        ## Points legend
            </ul>
                    <div id="map-polygons-list-${field.title}">
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
                        <input class="with-gap js-base-map-layers" name="map-base-layers-${field.title}" type="radio"
                               id="satelliteMapOption-${field.title}" value="satelliteMap" checked="checked"/>
                        <label for="satelliteMapOption-${field.title}">${_('Google Earth satellite images')}</label>
                    </p>
                    <p>
                        <input class="with-gap js-base-map-layers" name="map-base-layers-${field.title}" type="radio"
                               id="esriSatelliteMapOption-${field.title}" value="esriSatellite"/>
                        <label for="esriSatelliteMapOption-${field.title}">${_('ESRI World Imagery')}</label>
                    </p>
                    <p>
                        <input class="with-gap js-base-map-layers" name="map-base-layers-${field.title}" type="radio"
                               id="terrainMapOption-${field.title}" value="terrainMap"/>
                        <label for="terrainMapOption-${field.title}">${_('Google Terrain Map')}</label>
                    </p>
                    <p>
                        <input class="with-gap js-base-map-layers" name="map-base-layers-${field.title}" type="radio"
                               id="streetMapOption-${field.title}" value="streetMap"/>
                        <label for="streetMapOption-${field.title}">${_('OpenStreetMap')}</label>
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
                <form action="#" id="context-layers-list-${field.title}">
                    ## Context layers entries
          </form>
            </div>
        </li>
    </ul>
</div>

## Map modal (used for legend of context layers)

<div id="map-modal-${field.title}" class="modal">
    <div id="map-modal-body-${field.title}" class="modal-content">
        ## Placeholder for map modal
  </div>
    <div class="modal-footer">
        <a href="#" class="modal-action modal-close waves-effect waves-green btn-flat">${_('Close')}</a>
    </div>
</div>

## Filter (only once per page)

## <ul id="slide-out-filter-${field.title}" class="side-nav map-side-menu">
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
                                            data-tooltip="${_('Click on the map to set the location. Please zoom in to set the point as accurately as possible.')}"></span>
        <p style="margin-top: 10px;">${_('Please use the QGIS plugin to add or edit polygons.')} <a
                href="http://lokp.readthedocs.org/en/latest/qgis.html" target="_blank"
                class="text-accent-color">${_('Read more.')}</a></p>
    </div>
    <div class="input-field col s12" action="">
        <div class="col s6" style="margin: 0; padding: 0;">
            <a class="pointer btn tooltipped" onClick="javascript:triggerCoordinatesDiv();" data-position="top"
               data-delay="50"
               data-tooltip="${_('If you have GPS coordinates you can enter them to set the location even more accurately.')}">${_('Enter coordinates')}
                <i class="material-icons tooltipped right">my_location</i></a>
        </div>
        <div class="col s6" style="margin: 0; padding: 0;">
            <input id="js-map-search" data-set-marker="true" name="q" type="text" placeholder="${_('Search location')}"
                   style="line-height: 30px; height: 30px;">
            <button value="Search" id="search-submit" class="btn tooltipped" style="line-height: 30px; height: 30px;"
                    name="action" data-position="top" data-delay="50"
                    data-tooltip="${_('Start to search for a location by typing in the search field.')}"><i
                    class="material-icons">search</i></button>
        </div>
    </div>
</div>

<script type="text/javascript">
    var tForSuccess = "${_('Success!')}";
    var tForInvalidFormat = "${_('Not in a valid format!')}";
</script>
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
                    onClick="javascript:return parseCoordinates();">${_('Parse')}</button>
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
    console.log(deform);
    deform.addCallback(
            '${field.title}',
            function (oid) {
                createFormMap(oid, {pointsVisible: true, pointsCluster: true, geometry_type: ${geometry_type}}); // get geometry_type variable from python
            }
    );
</script>
