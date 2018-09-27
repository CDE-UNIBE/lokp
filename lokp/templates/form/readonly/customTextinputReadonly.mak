<div class="row-fluid">
    <div class="span4">
        <p>${field.title}</p>
    </div>
    <div class="span8">
        <input
            type="text"
            class="input-style span12"
            readonly="readonly"
            name="${field.name}"
            value="${cstruct}"
            id="${field.oid}"
            placeholder="-" />
        % if helptext:
            <div class="input-description">${helptext}</div>
        % endif
    </div>
</div>
