<%inherit file="lmkp:customization/lo/templates/base.mak" />

<%def name="title()">${_('About')}</%def>

<%def name="head_tags()">
<style type="text/css" >
    ul.about {
        list-style-type: disc;
        margin: 0 25px 15px;
    }
    ul.about li {
        margin: 5px 0;
    }
    .introvideo {
        margin-top: 40px;
    }
</style>

<script type="text/javascript"> <!--
    function UnCryptMailto( s )
    {
        var n = 0;
        var r = "";
        for( var i = 0; i < s.length; i++)
        {
            n = s.charCodeAt( i );
            if( n >= 8364 )
            {
                n = 128;
            }
            r += String.fromCharCode( n - 1 );
        }
        return r;
    }

    function linkTo_UnCryptMailto( s )
    {
        location.href=UnCryptMailto( s );
    }
    // --> </script>
</%def>

<div class="container">
    <div class="content no-border">

        <p class="lead">
            ${_('The Land Observatory is a pilot project of some of the partners of the Land Matrix initiative, to support observatories designed to crowdsource data about land deals, allowing for greater transparency and improved decision-making.')}
        </p>
        <p>
            ${_('We are co-creating software with partner organizations in pilot countries that will allow for them to')}
        </p>
        <ul class="about">
            <li>${_('generate greater spatial context for land deals')}</li>
            <li>
                ${_('make possible deeper investigation of the actors involved')}
            </li>
            <li>
                ${_('increase citizen participation, crowdsource and ground-truth data')}
            </li>
            <li>
                ${_('locally manage data on land deals')}
            </li>
        </ul>
        <p>
            ${_('We are piloting this project in five countries - Cambodia, Laos, Madagascar, Peru and Tanzania, with civil society partners and governments who will work to open government data, crowdsource and help customize local observatories using our software.')}
        </p>
        <p>
            ${_('The project is not merely technical, we are accompanying partners as they test different crowdsourcing strategies. Partners and their extended networks play a crucial role in bringing the online information to the real world, and back again.')}
        </p>
        <p>
            ${_('Updated information on land will benefit citizens, but also governments and companies interested in sustainability.')}
        </p>
        <p>
            ${_('If you are experiencing any technical difficulties, have questions or would like to send us feedback about how to improve user experience, please email us:')} <a href="javascript:linkTo_UnCryptMailto('nbjmup;mboe`pctfswbupszAvojcf/def/di');">land_observatory@unibe.cde.ch</a>
        </p>

        <div class="introvideo text-center">
            <iframe width="560" height="315" src="//www.youtube.com/embed/aYKnZOr6NdM?rel=0" frameborder="0" allowfullscreen></iframe>
            <p>
                ${_('View our brief video introduction')} (<a href="https://www.youtube.com/watch?v=aYKnZOr6NdM">${_('Click here if the embedded video is not working')}</a>).
            </p>
        </div>
    </div>
</div>

