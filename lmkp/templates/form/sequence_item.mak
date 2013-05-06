% if not field.widget.hidden:
<li
    % if field.error and field.widget.error_class:
        class="field ${field.widget.error_class}"
    % else:
        class="field"
    % endif
    title="${field.description}"
    i18n:domain="deform">

    <!-- sequence_item -->

    <span class="deformCloseButton"
          id="${field.oid}-close"
          title="Remove"
          onClick="javascript:deform.removeSequenceItem(this);"
    >
    </span>

    <span class="deformOrderButton"
          id="${field.oid}-order"
          title="Reorder (via drag and drop)"
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
                i18n:translate=""
            >${msg}</p>
        % endfor
    % endif

    <!-- /sequence_item -->

</li>
% endif