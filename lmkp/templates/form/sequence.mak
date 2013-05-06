<%
    now_len = len(subfields)
    min_len = field.widget.min_len if field.widget.min_len is not None else 0
    max_len = field.widget.max_len if field.widget.max_len is not None else 100000
    orderable = 1 if field.widget.orderable is True else 0
%>

<div class="deformSeq"
     id="${field.oid}">

     <!-- sequence -->

    <input type="hidden"
           name="__start__"
           value="${field.name}:sequence"
           class="deformProto"
           prototype="${field.widget.prototype(field)}"
    />

    <ul id="${field.oid}-orderable">

        <!--! subfields is a tuple for bw compat with 3rdparty templates;
              we ignore the first element (the cstruct) because it's already
              attached to the field -->
        % for subfield in subfields:
            ${subfield[1].render_template(field.widget.item_template, parent=field)}
        % endfor

        <span class="deformInsertBefore"
              min_len="${min_len}"
              max_len="${max_len}"
              now_len="${now_len}"
              orderable="${orderable}"
        >
        </span>

    </ul>

    <a href="#"
       class="deformSeqAdd"
       id="${field.oid}-seqAdd"
       onClick="javascript: return deform.appendSequenceItem(this);"
    >
        <small id="${field.oid}-addtext">${add_subitem_text}</small>
    </a>

    <script type="text/javascript">
        deform.addCallback(
            '${field.oid}',
            function(oid) {
                oid_node = $('#'+ oid);
                deform.processSequenceButtons(
                    oid_node, ${min_len}, ${max_len}, ${now_len}, ${orderable}
                );
            }
        );
        % if orderable:
            $("#${field.oid}-orderable").sortable({handle: "span.deformOrderbutton"});
        % endif
    </script>

    <input type="hidden" name="__end__" value="${field.name}:sequence"/>

    <!-- /sequence -->

</div>