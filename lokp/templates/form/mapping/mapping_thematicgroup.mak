<%doc>
  Renders the container for a thematic group.
</%doc>

<div class="grid-area row-fluid editviewcontainer">
  <div class="span4">
    <h5 class="dealview_titel_investor text-accent-color">${field.title}</h5>
  </div>
  <div class="span8">
    ${field.serialize(cstruct)}
  </div>
</div>
