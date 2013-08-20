
    % if field.title:
        <legend>${field.title}</legend>
    % endif

    <div id="googleMapNotFull" style="height:300px;"></div>

    <%
        from mako.template import Template
        from pyramid.path import AssetResolver
        import colander
        lmkpAssetResolver = AssetResolver('lmkp')
        resolver = lmkpAssetResolver.resolve('templates/map/mapform.mak')
        template = Template(filename=resolver.abspath())
        coords = None if cstruct['lon'] == colander.null or cstruct['lat'] == colander.null else [cstruct['lon'], cstruct['lat']]
        _ = request.translate
    %>

    ${template.render(request=request, coords=coords)}

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
        ${_('Set the location of the deal.')}<br/>
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
                    <option selected="selected" value="1">46&deg; 57.1578 N 7&deg; 26.1102 E</option>
                    <option value="2">46&deg 57' 9.468" N 7&deg 26' 6.612" E</option>
                    <option value="3">N 46&deg 57.1578 E 7&deg 26.1102</option>
                    <option value="4">N 46&deg 57' 9.468" E 7&deg 26' 6.612"</option>
                    <option value="5">46.95263, 7.43517</option>
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
