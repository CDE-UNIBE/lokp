<%inherit file="lmkp:customization/lo/templates/base.mak" />

<%def name="title()">${_(u"User Registration")}</%def>

<div class="container">
    <div class="content no-border">
        <h3>${_(u'Thank you for registering')}</h3>
        ${_(u'A message with an activation link has been sent to your email address. Your account will be approved after activation.')}
    </div>
</div>