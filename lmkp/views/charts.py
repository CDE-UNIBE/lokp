from pyramid.view import view_config
from pyramid.renderers import render_to_response

from lmkp.custom import get_customized_template_path
from lmkp.views.views import (
    BaseView,
    get_current_locale,
    get_current_profile,
)


class ChartsView(BaseView):

    @view_config(route_name='charts_overview')
    def charts_overview(self):

        self._handle_parameters()

        groupedBy = self.request.params.get('groupby', None)

        # TODO: Make this more dynamic.
        # TODO: Translation.
        groupableBy = [
            'Intention of Investment',
            'Negotiation Status',
            'Implementation status'
        ]

        alert = groupedBy is None

        groupedBy = groupedBy if groupedBy in groupableBy else groupableBy[0]

        return render_to_response(
            get_customized_template_path(self.request, 'charts/barchart.mak'),
            {
                'profile': get_current_profile(self.request),
                'locale': get_current_locale(self.request),
                'groupedBy': groupedBy,
                'groupableBy': groupableBy,
                'alert': alert
            },
            self.request)
