<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        ${self.head_tags()}
    </head>
    <body>
        <div id="header-div">
            <div id="title-div">
                <h1>
                    ${_("Land Observatory")}
                </h1>
                <p>
                    ${_("The Land Observatory will make information on large-scale land acquisition transparent and accessible through an interactive, map-based platform. We are piloting the project in five countries, with partners and governments who will work to open government data, crowdsource and help customize local observatories. Updated information on land will benefit citizens, but also governments and companies interested in sustainability.")}
                </p>
                <p>
                    ${_("The pilot project is coordinated by the")}
                    <a href="http://www.landcoalition.org/">${_("International Land Coalition")}</a>
                    ${_("and the")}
                    <a href="http://www.cde.unibe.ch/">${_("Centre for Development and Environment")}</a>
                    ${_("at the University of Bern, Switzerland. It is funded by the")}
                    <a href="http://www.sdc.admin.ch/">${_("Swiss Agency for Development Cooperation")}</a>
                    ${_(", with co-funding from other ILC and CDE programs.")}
                </p>
            </div>
            <div id="logo-div">
                <a href="http://www.landportal.info/observatory">
                    <img src="${request.static_url('lmkp:static/img/lo-logo.png')}" height="100" width="100" alt="${_('Land Observatory')}"/>
                </a>
            </div>
        </div>
        ${self.body()}
    </body>
</html>