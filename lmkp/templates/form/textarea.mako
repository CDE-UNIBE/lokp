<textarea id="${field.oid}"

        % if field.widget.rows:
            rows="${field.widget.rows}"
        % endif

        % if field.widget.cols:
            cols="${field.widget.cols}"
        % endif

        % if field.widget.css_class:
            class="${field.widget.css_class}"
        % endif

        % if field.widget.style:
            style="${field.widget.style}"
        % endif

          name="${field.name}"
>${cstruct}</textarea>
