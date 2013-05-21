% if not field.widget.hidden:
<li
    % if field.error and field.widget.error_class:
        class="field ${field.widget.error_class}"
    % else:
        class="field"
    % endif
    title="${field.description}">

    <!-- sequence_item -->

    <span class="deformCloseButton"
          id="${field.oid}-close"
          title="${_("Remove")}"
          onClick="javascript:deform.removeSequenceItem(this);"
    >
    </span>

    <span class="deformOrderButton"
          id="${field.oid}-order"
          title="${_("Reorder (via drag and drop)")}"
    >
    </span>

    ${field.serialize(cstruct=cstruct)}

    % if field.error:
        <%
            errstr = 'error-%s' % field.oid
        %>
        % for msg in field.error.messages():
            <p
                % if msg.index==0:
                    id="${errstr}"
                % else:
                    id="${'%s-%s' % (errstr, msg.index)}"
                % endif
                class="${field.widget.error_class}"
            >${_(msg)}</p>
        % endfor
    % endif

    <!-- /sequence_item -->

</li>
% endif