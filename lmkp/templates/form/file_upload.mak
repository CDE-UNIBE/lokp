${field.start_mapping()}

<div class="row-fluid">
    <div class="span4">
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
    <div class="span8">
        % if cstruct.get('uid'):
        <input type="hidden" name="uid" value="${cstruct['uid']}" id="${field.oid}-uid" />
        <span id="${oid}-filename">${cstruct['filename']}</span>
        % endif

        <input type="file" class="input-style fileInput" name="upload" id="${field.oid}"/>
    </div>
</div>

${field.end_mapping()}