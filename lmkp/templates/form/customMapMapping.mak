
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
        ${_('Click on the map to set the location of the deal. Please zoom in to set the point as accurately as possible.')}
    </p>

    ${field.start_mapping()}

    % for child in field.children:
        ${child.render_template(field.widget.item_template)}
    % endfor

    ${field.end_mapping()}
