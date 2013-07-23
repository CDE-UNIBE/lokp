<%
    """
    This is the main form view which is rendered for both Activities and
    Stakeholders, embedded or not.
    A swich decides which form to render.
    """

    from mako.template import Template
    from pyramid.path import AssetResolver
    lmkpAssetResolver = AssetResolver('lmkp')

    if cstruct['itemType'] == 'stakeholders':
        # Stakeholders
        if 'embedded' in cstruct:
            # Embedded
            templateName = 'form_stakeholder_embedded.mak'
        else:
            templateName = 'form_stakeholder.mak'
    else:
        # Activities
        templateName = 'form_activity.mak'

    resolver = lmkpAssetResolver.resolve('templates/form/%s' % templateName)
    template = Template(filename=resolver.abspath())
%>

${template.render(request=request, field=field, cstruct=cstruct)}

<div id="formModal" class="modal hide fade">
    <div class="modal-body">
        <!-- Placeholder for the content of the modal window -->
    </div>
    <div class="modal-footer">
        <button id="formModalClose" class="btn" data-dismiss="modal" aria-hidden="true">${_('Close')}</button>
    </div>
</div>