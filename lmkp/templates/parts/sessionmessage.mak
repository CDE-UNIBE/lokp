<%doc>

    Include this file to show messages stored in the session.
    The messages are stored in different queues:
    - notice [default]: shown with CSS class="alert-notice"
    - success: shown with CSS class="alert-success"
    - error: shown with CSS class="alert-error"
    
    Use request.session.flash(msg, [queue]) to add messages to the session.

</%doc>

## Error queue
% if request.session.peek_flash('error'):
    % for message in request.session.pop_flash('error'):
        <div class="alert alert-block alert-error">
            <button type="button" class="close" data-dismiss="alert">&times;</button>
            <% context.write(message) %>
        </div>
    % endfor
% endif
## Success queue
% if request.session.peek_flash('success'):
    % for message in request.session.pop_flash('success'):
        <div class="alert alert-block alert-success">
            <button type="button" class="close" data-dismiss="alert">&times;</button>
            <% context.write(message) %>
        </div>
    % endfor
% endif
## Default queue
% if request.session.peek_flash() or request.session.peek_flash('notice'):
    % for message in request.session.pop_flash():
        <div class="alert alert-block">
            <button type="button" class="close" data-dismiss="alert">&times;</button>
            <% context.write(message) %>
        </div>
    % endfor
    % for message in request.session.pop_flash('notice'):
        <div class="alert alert-block">
            <button type="button" class="close" data-dismiss="alert">&times;</button>
            <% context.write(message) %>
        </div>
    % endfor
% endif