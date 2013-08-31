<%inherit file="lmkp:customization/lo/templates/base.mak" />

<%def name="title()">${_(u"User Activation Success")}</%def>


<div class="container">
    <div class="content no-border">
        <h3>${_(u"User activation was successful:")} ${username}</h3>
        <div>
            ${_(u"Your account has been activated. It will be approved during the next days.")}
        </div>
    </div>
</div>