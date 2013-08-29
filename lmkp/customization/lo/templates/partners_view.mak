<%inherit file="lmkp:customization/lo/templates/base.mak" />

<%def name="title()">${_('Partners & Donors')}</%def>

<div class="container">
    <div class="content no-border">
        <h3>
            ${_('Partners & Donors')}
        </h3>

        <p>${_('The pilot project is coordinated by the International Land Coalition and the Centre for Development and Environment at the University of Bern, Switzerland. It is funded by the Swiss Agency for Development Cooperation, with co-funding from other ILC and CDE programs.')}</p>

        <p>&nbsp;</p>
        <p>&nbsp;</p>

        <div class="row-fluid">
            <div class="span4 text-left">
                <a href="http://www.landcoalition.org/" target="_blank">
                    <img src="${request.static_url('lmkp:static/img/logos/ilc.png')}" />
                </a>
            </div>
            <div class="span4 text-center">
                <a href="http://www.cde.unibe.ch/" target="_blank">
                    <img src="${request.static_url('lmkp:static/img/logos/cde.jpg')}" />
                </a>
            </div>
            <div class="span4 text-right">
                <a href="http://www.sdc.admin.ch/" target="_blank">
                    <img src="${request.static_url('lmkp:static/img/logos/sdc.jpg')}" />
                </a><br/>
                <a href="http://www.fordfoundation.org/" target="_blank">
                    <img src="${request.static_url('lmkp:static/img/logos/fordfoundation.png')}" />
                </a>
            </div>
        </div>

    </div>
</div>

