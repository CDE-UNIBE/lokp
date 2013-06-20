<h3>Deal Details</h3>

% if 'id' in cstruct:
    <p class="id">${cstruct['id']}</p>
% endif

## Map container
<div class="row-fluid">
    <div class="span9 map-not-whole-page">
        <div id="googleMapNotFull"></div>
    </div>
</div>

% for child in field:
    ${child.render_template(field.widget.readonly_item_template)}
% endfor

% if 'id' in cstruct:
    <a href="/activities/form/${cstruct['id']}">
        <i class="icon-pencil"></i>&nbsp;&nbsp;Edit this deal
    </a>
% endif