<div class="row-fluid">
    <div class="span4">
        <p>${field.name}</p>
    </div>
    <div class="span6">
        <input
            type="text"
            class="input-style"
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