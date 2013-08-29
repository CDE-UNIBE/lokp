<%inherit file="lmkp:customization/lo/templates/base.mak" />

<%def name="title()">Charts View</%def>

<%def name="head_tags()">
<style type="text/css" >
    .chartGalleryDescription {
        margin-top: 1em;
    }
</style>
</%def>

<div class="container">
    <div class="content no-border">

        <h3>Charts</h3>

        <p>Place some meaningful content here ...</p>

        <div class="row-fluid chartGallery">
            <div class="span4">
                <a href="${request.route_url('charts_overview')}">
                    <img src="${request.static_url('lmkp:static/img/charts/overview_thumbnail_medium.png')}" class="img-polaroid" />
                    <p class="chartGalleryDescription text-center">Overview</p>
                </a>
            </div>
        </div>
    </div>
</div>

