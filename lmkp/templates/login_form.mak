<%
mode = None
if 'lmkp.mode' in request.registry.settings:
    if str(request.registry.settings['lmkp.mode']).lower() == 'demo':
        mode = 'demo'
%>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <title>
            ${_("Land Observatory")} - ${_(u"Login")}
            % if mode == 'demo':
                ${_("[Demo]")}
            % endif
        </title>
        <link rel="stylesheet" type="text/css" href="${request.static_url('lmkp:static/style.css')}"></link>
    </head>
    <body>
        <div class="login">
            <a href="/">
                <img src="${request.static_url('lmkp:static/img/lo-logo.png')}" alt="${_(u'Land Observatory')}"/>
            </a><br/>
            ${_(u"Login to the Land Observatory")}
        </div>
        % if warning is not None:
        <div class="login login-warning">
            ${warning | n}
        </div>
        % endif
        <div>
            <form action="/login" method="POST">
                <fieldset class="simple_login">
                    <label for="login">${_(u"Username")}:</label>
                    <input class="simple_login" type="text" id="login" name="login" /><br />
                    <label for="password">${_(u"Password")}:</label>
                    <input class="simple_login" type="password" id="password" name="password" /><br/>
                    <input type="hidden" name="came_from" value="${came_from}"/><br />
                    <input type="submit" name="form.submitted" value="Login"/>
                </fieldset>
            </form>
        </div>
        % if mode != 'demo':
            <div class="login">
                <a href="/reset">${_(u"Forgot Password?")}</a>
            </div>
        % else:
            <div class="demo-instructions">
                <h3>
                    ${_(u"Welcome to the demonstration version of the Land Observatory.")}
                </h3>
                    ${_(u"Any member of the public can log-in as an Editor or a Moderator.")}
                    <ul>
                        <p><b>${_(u"Editor")}</b>${_(u" has the permission to create or edit new Deals or Stakeholders")}</p>
                        <ul>
                            ${_(u"Username")}: editor<br/>${_(u"Password")}: editor
                        </ul>
                    </ul>
                    <ul>
                        <p><b>${_(u"Moderator")}</b>${_(u" has the additional permission to review pending changes in the global profile")}:</p>
                        <ul>
                            ${_(u"Username")}: moderator<br/>${_(u"Password")}: moderator
                        </ul>
                    </ul>
                <p>
                    ${_(u"This demo version is for learning and experimentation purposes, so first-time users can get a feel for the Observatory and its functions.")}
                </p>
                <p>
                    ${_(u"New data added by users to the demo has not been verified in any way. It will be visible to the public, but deleted every 24 hours.")}
                </p>
                <p>
                    ${_(u"We will be releasing the official, public version of the Observatory soon.")}
                </p>
                <p>
                    ${_(u"Please send your questions and feedback on the Observatory to: ")}<a href="mailto:info_landobservatory@cde.unibe.ch">info_landobservatory@cde.unibe.ch</a>
                </p>
            </div>
        % endif
    </body>
</html>