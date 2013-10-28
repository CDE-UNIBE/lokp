<%
    from mako.template import Template
    from pyramid.path import AssetResolver
    from lmkp.config import getTemplatePath
    import colander
    lmkpAssetResolver = AssetResolver('lmkp')
    resolver = lmkpAssetResolver.resolve('templates/map/mapform.mak')
    template = Template(filename=resolver.abspath())
    activitiesResolver = lmkpAssetResolver.resolve(getTemplatePath(request, 'parts/items/activities.mak'))
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
                        <a class="btn btn-mini active ttip" id="btn-add-point" data-toggle="tooltip" title="${_('Add a location to the deal')}"><i class="icon-plus"></i></a>
                        <a class="btn btn-mini ttip" id="btn-remove-point" data-toggle="tooltip" title="${_('Remove a location from the deal')}"><i class="icon-minus"></i></a>
                        <a class="btn btn-mini btn-danger disabled ttip disableClick"><i class="icon-pencil"></i></a>
                    </div>
                </div>
            % endif

            <div class="form-map-menu pull-right">
                <button type="button" class="btn btn-mini pull-right form-map-menu-toggle ttip" data-close-text="<i class='icon-remove'></i>" data-toggle="tooltip" title="${_('Turn layers on and off')}"><i class="icon-cog"></i></button>
                <div class="accordion" id="form-map-menu-content">
                    <!-- Base layers -->
                    <div class="accordion-group">
                        <h6>
                            <a class="accordion-toggle" data-toggle="collapse" data-parent="#form-map-menu-content" href="#baseLayers">
                                <b class="caret"></b>${_('Base layers')}
                            </a>
                        </h6>
                        <div id="baseLayers" class="accordion-body collapse">
                            <ul>
                                <li>
                                    <label class="radio inline"><input type="radio" class="baseMapOptions" name="baseMapOptions" id="streetMapOption" value="streetMap" />${_('Street Map')}</label>
                                </li>
                                <li>
                                    <label class="radio inline"><input type="radio" class="baseMapOptions" name="baseMapOptions" id="satelliteMapOption" value="satelliteMap" checked="checked" />${_('Satellite Imagery')}</label>
                                </li>
                                <li>
                                    <label class="radio inline"><input type="radio" class="baseMapOptions" name="baseMapOptions" id="terrainMapOption" value="terrainMap" />${_('Terrain Map')}</label>
                                </li>
                            </ul>
                        </div>
                    </div>
                    <!-- Context layers -->
                    <div class="accordion-group">
                        <h6>
                            <a class="accordion-toggle" data-toggle="collapse" data-parent="#form-map-menu-content" href="#contextLayers">
                                <b class="caret"></b>${_('Context layers')}
                            </a>
                        </h6>
                        <div id="contextLayers" class="accordion-body collapse">
                            <ul id="context-layers-list">
                                  <!-- Placeholder for context layers entries -->
                            </ul>
                        </div>
                    </div>
                    <!-- Activity layers -->
                    <div class="accordion-group">
                        <h6>
                            <a class="accordion-toggle" data-toggle="collapse" data-parent="#form-map-menu-content" href="#activityLayers">
                                <b class="caret"></b>${activitiesTemplate.render(request=request, _=_)}
                            </a>
                        </h6>
                        <div id="activityLayers" class="accordion-body collapse">
                            <ul>
                                <li>
                                    <div class="checkbox-modified-small">
                                        <input type="checkbox" id="activityLayerToggle" class="input-top">
                                        <label for="activityLayerToggle"></label>
                                    </div>
                                    <p class="context-layers-description">
                                        ${_('Show on map')}
                                    </p>
                                </li>
                            </ul>
                            <div id="map-legend-list">
                                <!-- Placeholder for legend -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

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

    <div class="row-fluid" style="margin-top: 10px;">
        <div class="span6">
            % if field.required:
                <span class="required-form-field"></span>
            % endif
            ${_('Set the location')}&nbsp;<span class="helpTooltip icon-question-sign ttip-bottom" data-toggle="tooltip" title="${_('Click on the map to set the location. Please zoom in to set the point as accurately as possible.')}"></span>
        </div>
        <div class="span6 text-right">
            <div class="navbar-search pull-right text-left" action="">
                <input name="q" id="search" class="search-query" placeholder="${_('search location')}" />
                <input value="Search" id="search-submit" class="ttip-bottom" data-toggle="tooltip" title="${_('Start to search for a location by typing in the search field.')}" />
            </div>
            <div class="pull-right" style="margin-top: 10px;">
                <a class="pointer" onClick="javascript:triggerCoordinatesDiv();">${_('Enter coordinates')}</a>&nbsp;<span class="helpTooltip icon-compass ttip-bottom" data-toggle="tooltip" title="${_('If you have GPS coordinates you can enter them to set the location even more accurately.')}"></span>
            </div>
        </div>
    </div>
        
    <script type="text/javascript">
        var tForSuccess = "${_('Success!')}";
        var tForInvalidFormat = "${_('Not in a valid format!')}";
    </script>
    <div id="coordinates-div" class="hide">
        <div class="row-fluid">
            <div class="span4">
                <label for="map-coords-field">${_('Coordinates')}</label>
            </div>
            <div class="span8">
                <input id="map-coords-field" class="input-style" type="text" />
            </div>
        </div>
        <div class="row-fluid">
            <div class="span4">
                <label for="map-coords-format">${_('Format')}</label>
            </div>
            <div class="span8">
                <select id="map-coords-format" class="span8">
                    <option value="1">46&deg; 57.1578 N 7&deg; 26.1102 E</option>
                    <option value="2">46&deg 57' 9.468" N 7&deg 26' 6.612" E</option>
                    <option value="3">N 46&deg 57.1578 E 7&deg 26.1102</option>
                    <option value="4">N 46&deg 57' 9.468" E 7&deg 26' 6.612"</option>
                    <option selected="selected" value="5">46.95263, 7.43517</option>
                </select>
            </div>
        </div>
        <div class="row-fluid">
            <div class="span4">
                <button id="map-coords-button" class="btn btn-small" onClick="javascript:return parseCoordinates();">${_('Parse')}</button>
            </div>
            <div id="map-coords-message" class="span8">
                <!-- Placeholder -->
            </div>
        </div>
    </div>

    ${field.start_mapping()}

    % for child in field.children:
        ${child.render_template(field.widget.item_template)}
    % endfor

    ${field.end_mapping()}
