<div class="deformSeq readonly">
    <ul>
        % for tup in subfields:
            ${field.render_template(field.widget.readonly_item_template, field=tup[1], cstruct=tup[0])}
        % endfor
    </ul>
</div>