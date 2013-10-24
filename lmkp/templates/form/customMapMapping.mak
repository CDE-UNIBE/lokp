<%
    from mako.template import Template
    from pyramid.path import AssetResolver
    import colander
    lmkpAssetResolver = AssetResolver('lmkp')
    resolver = lmkpAssetResolver.resolve('templates/map/mapform.mak')
    template = Template(filename=resolver.abspath())
    geometry = None if cstruct['geometry'] == colander.null else cstruct['geometry']
    editmode = None if cstruct['editmode'] == colander.null else cstruct['editmode']
    _ = request.translate
%>

    % if field.title:
        <legend>${field.title}</legend>
    % endif

    <div id="googleMapNotFull" style="height:300px;">

        % if editmode == 'multipoints':
            <div class="form-map-edit pull-right">
                <div class="btn-group pull-right" data-toggle="buttons-radio">
                    <a class="btn btn-mini active ttip" id="btn-add-point" data-toggle="tooltip" title="${_('Add a new point to the map')}"><i class="icon-plus"></i></a>
                    <a class="btn btn-mini ttip" id="btn-remove-point" data-toggle="tooltip" title="${_('Remove a point from the map')}"><i class="icon-minus"></i></a>
                    <a class="btn btn-mini btn-danger disabled ttip"><i class="icon-pencil"></i></a>
                </div>
            </div>
        % endif

        <div class="form-map-menu pull-right">
            <button type="button" class="btn btn-mini pull-right form-map-menu-toggle ttip" data-toggle="button tooltip" title="${_('Turn layers on and off')}"><i class="icon-cog"></i></button>
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
            </div>
        </div>
    </div>

    ${template.render(request=request, geometry=geometry, editmode=editmode)}

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

    <p style="margin-top: 10px;">
        % if field.required:
            <span class="required-form-field"></span>
        % endif
        ${_('Set the location.')}<br/>
        ${_('Click on the map to set the location. Please zoom in to set the point as accurately as possible.')}<br/>
        <a href="#" onClick="javascript:triggerCoordinatesDiv();">${_('Enter coordinates.')}</a>
    </p>
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
