<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
    <head>

        <%
            if 'scripts/jquery-ui-1.8.11.custom.min.js' not in js_links:
                js_links.append('scripts/jquery-ui-1.8.11.custom.min.js')
        %>

        % for reqt in js_links:
            <script type="text/javascript" src="/formstatic/${reqt}"></script>
        % endfor

        <script type="text/javascript" src="${request.static_url('lmkp:static/v2/stakeholderformembedded.js')}"></script>
        <script type="text/javascript" src="${request.static_url('lmkp:static/media/js/vendor/bootstrap.min.js')}"></script>
    </head>

    <body>

        % if js and success is True:

            ## Store the data of the newly created Stakeholder so it can be
            ## inserted in the readonly fields.
            <script type="text/javascript">
                ${js | n}
            </script>
            
            <h4>Success</h4>
            <p>The Stakeholder was successfully created. It will be reviewed shortly.</p>

        % elif success is False:
            ## The form was rerendered becaues it contains errors
            <div id="create-new-stakeholder">
                ${form | n}
            </div>
            <script type="text/javascript">
                createNewStakeholder();
            </script>

        % else:
            <div id="select-stakeholder">
                <h4>Select a Stakeholder</h4>
                <p>
                    Select an existing Stakeholder.
                </p>
                <p>
                    Start typing (at least 4 characters) to search a Stakeholder by name.
                </p>
                <input type="text" tabindex="1" id="shselectinput" placeholder="Search ..."/>

                <hr class="lightgray" />

                <p>
                    Stakeholder not found?
                </p>
                <p>
                    <a
                        id="create-new-stakeholder"
                        href=""
                        class="btn"
                        onclick="return createNewStakeholder();">
                        Create a new Stakeholder
                    </a>
                </p>
            </div>

            <div id="create-new-stakeholder">
                ${form | n}
            </div>

            <div id="stakeholderFormLoading" class="hide">
                Sending ...
            </div>
        % endif



        <script type="text/javascript">
            deform.load();

            var unknownString = 'Unknown';
            var queryUrl = "${request.route_url('stakeholders_read_many', output='json')}"

            $('button#create-new-stakeholder').click(function() {
                hideButtons();
                $('div#create-new-stakeholder').show();
            });
        </script>

    </body>
</html>

