<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <title>Login</title>
        <link rel="stylesheet" type="text/css" href="${request.static_url('lmkp:static/style.css')}"></link>
    </head>
    <body>
        <div>
            <form action="/login" method="POST">
                <fieldset class="simple_login">
                    <label for="login">Username:</label>
                    <input class="simple_login" type="text" id="login" name="login" /><br />
                    <label for="password">Password:</label>
                    <input class="simple_login" type="password" id="password" name="password" /><br/>
                    <input type="hidden" name="came_from" value="${came_from}"/><br />
                    <input type="submit" name="form.submitted" value="Login"/>
                </fieldset>
            </form>
        </div>
    </body>
</html>