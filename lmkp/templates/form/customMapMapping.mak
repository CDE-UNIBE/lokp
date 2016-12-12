<%
    from mako.template import Template
    from pyramid.path import AssetResolver
    from lmkp.custom import get_customized_template_path
    import colander
    lmkpAssetResolver = AssetResolver('lmkp')
    resolver = lmkpAssetResolver.resolve('templates/map/mapform.mak')
    template = Template(filename=resolver.abspath())
    activitiesResolver = lmkpAssetResolver.resolve(get_customized_template_path(request, 'parts/items/activities.mak'))
    activitiesTemplate = Template(filename=activitiesResolver.abspath())
    geometry = None if cstruct['geometry'] == colander.null else cstruct['geometry']
    editmode = None if cstruct['editmode'] == colander.null else cstruct['editmode']
    _ = request.translate
%>

    % if field.title:
        <legend>${field.title}</legend>
    % endif
    <div id="googleMapNotFull">

        <div class="map-form-controls">

            % if editmode == 'multipoints':
                <div class="form-map-edit pull-right">
                    <div class="btn-group pull-right" data-toggle="buttons-radio">
                        <a class="btn btn-mini active ttip" id="btn-add-point" data-toggle="tooltip" title="${_('Add a location to the map')}"><i class="icon-plus"></i></a>
                        <a class="btn btn-mini ttip" id="btn-remove-point" data-toggle="tooltip" title="${_('Remove a location from the map')}"><i class="icon-minus"></i></a>
                        <a class="btn btn-mini btn-danger disabled ttip disableClick"><i class="icon-pencil"></i></a>
                    </div>
                </div>
            % endif

            <div class="form-map-menu pull-right">
                <a class="btn-floating tooltipped btn-large button-collapse" style="margin-right: 15px; margin-top: 15px;" data-position="top" data-tooltip="${_('Turn layers on and off')}" data-activates="slide-out-map-options">
                    <i class="material-icons">map</i>
                </a>
            </div>
        </div>
    </div>



    <ul id="slide-out-map-options" class="side-nav" style="min-width: 550px; z-index: 10000;">

        <ul class="collapsible" data-collapsible="accordion">
            <!-- Deals -->
            <li>
                <div class="collapsible-header"><i class="material-icons">group</i>${_('Deals')}</div>
                <div class="collapsible-body">
                    <form action="#" id="map-areas-list">
                        <p style="padding-top: 0; padding-bottom: 0; margin: 0;">
                            <input class="input-top" type="checkbox" id="activityLayerToggle" checked="checked" style="line-height: 22px; height: 22px; background-color: red;">
                            <label class="text-primary-color" for="activityLayerToggle" style="line-height: 22px; height: 22px;">
                                <span id="map-deals-symbolization">

                                </span>
                            </label>
                            <ul id="map-points-list" style="margin: 0; padding: 0; padding-left: 100px;">
                            <!-- Placeholder for map points -->
                            </ul>
                        </p>
                    </form>
                </div>
            </li>


            <!-- Base layers -->
            <li>
                <div class="collapsible-header"><i class="material-icons">map</i>${_('Base layers')}</div>
                <div class="collapsible-body">
                    <form action="#">
                        <p style="padding-top: 0; padding-bottom: 0;">
                          <input class="with-gap baseMapOptions" name="baseMapOptions" type="radio" id="streetMapOption" value="streetMap" checked/>
                          <label for="streetMapOption">${_('Street Map')}</label>
                        </p>
                        <p style="padding-top: 0; padding-bottom: 0;">
                          <input class="with-gap baseMapOptions" name="baseMapOptions" type="radio" id="satelliteMapOption" value="satelliteMap" />
                          <label for="satelliteMapOption">${_('Satellite Imagery')}</label>
                        </p>
                        <p style="padding-top: 0; padding-bottom: 0;">
                          <input class="with-gap baseMapOptions" name="baseMapOptions" type="radio" id="terrainMapOption" value="terrainMap" />
                          <label for="terrainMapOption">${_('Terrain Map')}</label>
                        </p>
                    </form>
                </div>
            </li>
            <!-- Context layers -->
            <li>
                <div class="collapsible-header"><i class="material-icons">layers</i>${_('Context layers')}</div>
                <div class="collapsible-body">
                    <form action="#" id="context-layers-list">
                        <!--  Placeholder context layer entries -->
                    </form>
                </div>
            </li>
        </ul>
    </ul>



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
            ${_('Set the location')}&nbsp;<span class="helpTooltip icon-question-sign tooltipped" data-position="top" data-delay="50" data-tooltip="${_('Click on the map to set the location. Please zoom in to set the point as accurately as possible.')}"></span>
            <p style="margin-top: 10px;">${_('Please use the QGIS plugin to add or edit polygons.')} <a href="http://lokp.readthedocs.org/en/latest/qgis.html" target="_blank" class="text-accent-color">${_('Read more.')}</a></p>
        </div>
        <div class="input-field col s12" action="">
            <div class="col s6" style="margin: 0; padding: 0;">
                <a class="pointer btn tooltipped" onClick="javascript:triggerCoordinatesDiv();" data-position="top" data-delay="50" data-tooltip="${_('If you have GPS coordinates you can enter them to set the location even more accurately.')}">${_('Enter coordinates')}<i class="material-icons tooltipped right">my_location</i></a>
            </div>
            <div class="col s6" style="margin: 0; padding: 0;">
                <input id="search" name="q" type="text" placeholder="${_('Search location')}" style="line-height: 30px; height: 30px;">
                <button value="Search" id="search-submit" class="btn tooltipped" style="line-height: 30px; height: 30px;" name="action" data-position="top" data-delay="50" data-tooltip="${_('Start to search for a location by typing in the search field.')}"><i class="material-icons">search</i></button>
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
                <input id="map-coords-field" class="input-style" type="text" />
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
                <button id="map-coords-button" class="btn btn-small" onClick="javascript:return parseCoordinates();">${_('Parse')}</button>
            </div>
            <div id="map-coords-message" class="col s8">
                <!-- Placeholder -->
            </div>
        </div>
    </div>

    ${field.start_mapping()}

    % for child in field.children:
        ${child.render_template(field.widget.item_template)}
    % endfor

    ${field.end_mapping()}
