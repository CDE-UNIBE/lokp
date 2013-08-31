<%inherit file="lmkp:customization/lo/templates/base.mak" />

<%def name="title()">${_('FAQ')}</%def>

<%def name="head_tags()">
<style type="text/css" >
    ul.bullets {
        list-style-type: disc;
        margin: 0 25px 15px;
    }
    ul.bullets li {
        margin: 5px 0;
    }
    ul.links {
        margin: 20px 0;
    }
    ul.links li {
        line-height: 1.8em;
    }
</style>
</%def>

<%
    from lmkp.views.form_config import getCategoryList
    cList = getCategoryList(request, 'activities')
    desiredKeys = cList.getDesiredKeyNames()
%>

<div class="container">
    <div class="content no-border">
        <h3>
            ${_('FAQ')}
        </h3>
            <ul class="links">
                <li><a href="#q1">${_('Why are there observatories in only five countries?')}</a></li>
                <li><a href="#q2">${_('Who "owns" each observatory in the five pilot countries?')}</a></li>
                <li><a href="#q3">${_('Can I comment on a land deal?')}</a></li>
                <li><a href="#q4">${_('How do I submit information on a land deal?')}</a></li>
                <li><a href="#q5">${_('Can I submit information on a land deal even if I am in a different country?')}</a></li>
                <li><a href="#q6">${_('Will this application display polygons and land areas?')}</a></li>
                <li><a href="#q7">${_('Do you protect my privacy?')}</a></li>
            </ul>
        <hr class="grey" />

        <a name="q2"></a><p class="lead">${_('Why are there observatories in only five countries?')}</p>
        <p>${_('We are piloting this project in five countries. More than just testing software, this requires partners to design crowdsourcing campaigns and organise multi-stakeholder platforms to manage the observatories. These are all very intensive processes and need time. We plan to scale, and seed observatories in other countries in the near future.')}</p>
        <hr class="grey" />

        <a name="q1"></a><p class="lead">${_('Who "owns" each observatory in the five pilot countries?')}</p>
        <p>${_('We have co-developed this software with partners in country, and we are still firming up formal arrangements with partner organisations, and where possible with governments. Generally speaking, each observatory will have its own governance structure and moderation team and procedures. More information will be made available soon about each country.')}</p>
        <hr class="grey" />

        <a name="q3"></a><p class="lead">${_('Can I comment on a land deal?')}</p>
        <p>${_('Anybody, even anonymous, non-logged in users can comment on a land deal. These comments will be subject to the rules of moderation, unique to each observatory.')}</p>
        <hr class="grey" />

        <a name="q4"></a><p class="lead">${_('How do I submit information on a land deal?')}</p>
        <p>${_('If you have information about a land deal in one of the five pilot countries, you can submit information about one or more attributes of this deal. You can also submit a new land deal if the one you are concerned with does not appear on the map.')}
            ${_('You will need to')} <a href="${request.route_url('user_self_registration')}">${_('register')}</a> ${_('(giving us your email) and')} <a href="${request.route_url('login')}">${_('log-in')}</a>.</p>
        <p>${_('After you submit, moderators will review and approve your report. New deals will not be approved until all of the mandatory attributes are completed.')}</p>
        <ul class="bullets">
            % for k in desiredKeys:
            <li>${k}</li>
            % endfor
        </ul>
        <p>${_('Once your report is reviewed and approved, it is public for the whole world to see.')}</p>
        <hr class="grey" />

        <a name="q5"></a><p class="lead">${_('Can I submit information on a land deal even if I am in a different country?')}</p>
        <p>${_('Yes, but it will be reviewed and approved by moderators. At the moment, we ask that your account is connected to a particular country.')}</p>
        <hr class="grey" />

        <a name="q6"></a><p class="lead">${_('Will this application display polygons and land areas?')}</p>
        <p>${_('Yes, these functions are in development and should be ready soon, as well as data downloads.')}</p>
        <hr class="grey" />
        
        <a name="q7"></a><p class="lead">${_('Do you protect my privacy?')}</p>
        <p>${_('All defaults are set to safeguard user privacy. To comment, you need not give any personal information, although providing it may enhance your credibility. To log-in and submit data, all you need to provide is an email address. Currently, metadata about your submissions is stored on the servers of the Centre for Development and Environment - University of Bern and are only kept for reference: your personal information will not be shared with others or re-used for any purposes except for possible verification of submitted information.')}</p>
        <hr class="grey" />

    </div>
</div>

