<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
    <head>
        % for reqt in js_links:
            <script type="text/javascript" src="/formstatic/${reqt}"></script>
        % endfor
    </head>

    <body>

        <div id="new-stakeholder-buttons">
            <button id="create-new-stakeholder">
                <span>Create a new Stakeholder</span>
            </button>
            <button id="select-existing-stakeholder">
                <span>Select an existing Stakeholder</span>
            </button>
        </div>

        <div id="create-new-stakeholder">
            ${form | n}
        </div>

        <div id="select-existing-stakeholder">
            coming soon ...
        </div>

        <script type="text/javascript">
            deform.load();

            $('button#create-new-stakeholder').click(function() {
                hideButtons();
                $('div#create-new-stakeholder').show();
            });

            $('button#select-existing-stakeholder').click(function() {
                hideButtons();
                $('div#select-existing-stakeholder').show();
            });

            function hideButtons() {
                $('div#new-stakeholder-buttons').hide();
            }

        </script>

    </body>
</html>


