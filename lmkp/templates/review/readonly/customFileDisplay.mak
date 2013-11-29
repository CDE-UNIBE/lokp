<%
    _ = request.translate
    ## Split the values (files are stored as comma-separated list of
    ## filename|fileidentifier)
    fileValues = []
    for values in cstruct.split(','):
        if values != '':
            fileValues.append(values.split('|'))
%>

% for v in fileValues:
<div class="fileDisplay">
<a href="${request.route_url('file_view', action='view', identifier=v[1])}" target="_blank">${v[0]}</a>
<span class="pull-right">
    <a href="${request.route_url('file_view', action='view', identifier=v[1])}" target="_blank" class="btn btn-mini"><i class="icon-eye-open" title="${_('View this file')}"></i></a>
    <a href="${request.route_url('file_view', action='download', identifier=v[1])}" target="_blank" class="btn btn-mini"><i class="icon-save" title="${_('Download this file')}"></i></a>
</span>
</div>
% endfor
