<div class="row-fluid">
    <div class="span4">
        <p>${field.name}</p>
    </div>
    <div class="span8">
        <textarea
            class="input-style"
            rows="4"
            id="${field.oid}"
            name="${field.name}"></textarea>
        % if helptext:
            <div class="input-description">${helptext}</div>
        % endif
    </div>
</div>
