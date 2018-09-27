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
        <div class="row">
          <div class="col s12">
            <div class="card-panel red">
              <span class="white-text"><% context.write(message) %></span>
            </div>
          </div>
        </div>
    % endfor
% endif
## Success queue
% if request.session.peek_flash('success'):
    % for message in request.session.pop_flash('success'):
        <div class="row">
          <div class="col s12">
            <div class="card-panel teal">
              <span class="white-text"><% context.write(message) %></span>
              <i class="material-icons right white-text" style="margin-top: -20px; cursor: pointer;" onclick="this.parentNode.parentNode.parentNode.style.display = 'none';">close</i>
            </div>
          </div>
        </div>
    % endfor
% endif
## Default queue
% if request.session.peek_flash() or request.session.peek_flash('notice'):
    % for message in request.session.pop_flash():
        <div class="row">
          <div class="col s12">
            <div class="card-panel teal">
                <span class="white-text"><% context.write(message) %></span>
                <i class="material-icons right white-text" style="margin-top: -20px; cursor: pointer;" onclick="this.parentNode.parentNode.parentNode.style.display = 'none';">close</i>
            </div>
          </div>
        </div>
    % endfor
    % for message in request.session.pop_flash('notice'):
        <div class="row">
          <div class="col s12">
            <div class="card-panel teal">
              <span class="white-text"><% context.write(message) %></span>
              <i class="material-icons right white-text" style="margin-top: -20px; cursor: pointer;" onclick="this.parentNode.parentNode.parentNode.style.display = 'none';">close</i>
            </div>
          </div>
        </div>
    % endfor
% endif
