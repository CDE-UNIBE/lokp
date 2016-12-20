${field.start_mapping()}

<div class="row" style="margin-top: 15px;">
    <div class="col s12">
        <label for="${field.oid}">
            % if field.title:
                ${field.title}
            % elif field.name:
                ${field.name}
            % endif
            % if field.required:
                <span class="required-form-field"></span>
            % elif desired:
                <span class="desired-form-field"></span>
            % endif
        </label>
    </div>
    <div class="col s12">
        % if cstruct.get('uid'):
        <input type="hidden" name="uid" value="${cstruct['uid']}" id="${field.oid}-uid" />
        <span id="${oid}-filename">${cstruct['filename']}</span>
        % endif

        <div class="file-field input-field">
          <div class="btn">
            <span>File</span>
            <input type="file" class="input-style fileInput" name="upload" id="${field.oid}"/>
          </div>
          <div class="file-path-wrapper">
            <input class="file-path validate" type="text">
          </div>
        </div>
    </div>
</div>

${field.end_mapping()}