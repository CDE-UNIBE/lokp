<%inherit file="lmkp:templates/htmlbase.mak" />

<%def name="title()">Land Observatory - Login</%def>

<%def name="head_tags()">
    ## TODO: This should be fixed in bootstrap
    <style type="text/css" >
        p.login-info {
            margin-left: 30px;
        }
    </style>
</%def>

<%
mode = None
if 'lmkp.mode' in request.registry.settings:
    if str(request.registry.settings['lmkp.mode']).lower() == 'demo':
        mode = 'demo'
%>

<div class="container">
    <div class="content no-border">
        <div class="row-fluid">
            <div class="span4 offset4">
                <h3>Login</h3>

                % if warning is not None:
                    <div class="alert alert-error">
                        ${warning | n}
                    </div>
                % endif
                <form action="/login" method="POST">
                    <fieldset class="simple_login">
                        <label for="login">${_(u"Username")}:</label>
                        <input class="input-style span12" type="text" id="login" name="login" /><br />
                        <label for="password">${_(u"Password")}:</label>
                        <input class="input-style span12" type="password" id="password" name="password" /><br/>
                        <input type="hidden" name="came_from" value="${came_from}"/><br />
                        <input class="btn btn-primary" type="submit" name="form.submitted" value="Login"/>
                    </fieldset>
                </form>

                % if mode != 'demo':
                <p>
                    <a href="/reset">${_(u"Forgot Password?")}</a>
                </p>
                <hr class="grey" />
                <p>
                    You do not have a password yet?<br/><a href="${request.route_url('user_self_registration')}">Register now!</a>
                </p>
            </div>
        </div>

                % else:
            </div>
        </div>
        <div class="row-fluid">
            <div class="span12">
                <h3>
                    ${_(u"Demo Version")}
                </h3>
                <p class="lead">This is the demonstration version of the <a href="http://www.landobservatory.org">Land Observatory</a>.</p>
                <p>${_(u"Any member of the public can log-in as an Editor or a Moderator.")}</p>

                <p><strong>Editor</strong> has the permission to create or edit new Deals or Stakeholders.</p>
                <p class="login-info">
                    Username: editor<br/>
                    Password: editor
                </p>

                <p><strong>Moderator</strong>  has the additional permission to review pending changes.</p>
                <p class="login-info">
                    Username: moderator<br/>
                    Password: moderator
                </p>

                <p>
                    ${_(u"This demo version is for learning and experimentation purposes, so first-time users can get a feel for the Observatory and its functions.")}
                </p>
                <p>
                    ${_(u"New data added by users to the demo has not been verified in any way. It will be visible to the public, but the database will be reset regularly.")}
                </p>
                <p>
                    ${_(u"Please send your questions and feedback on the Observatory to: ")}<a href="mailto:info_landobservatory@cde.unibe.ch">info_landobservatory@cde.unibe.ch</a>
                </p>
            </div>
        </div>
            % endif
    </div>
</div>