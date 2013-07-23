from pyramid.view import view_config

from lmkp.views.views import BaseView
from lmkp.views.profile import get_current_profile
from lmkp.views.profile import get_current_locale

class ChartsView(BaseView):

    @view_config(route_name='charts_overview', renderer='lmkp:templates/charts/barchart.mak')
    def charts_overview(self):

        self._handle_parameters()

        groupedBy = self.request.params.get('groupby', '')

        # TODO: Make this more dynamic.
        # TODO: Translation.
        groupableBy = [
            'Intention of Investment',
            'Negotiation Status',
            'Implementation status'
        ]

        groupedBy = groupedBy if groupedBy in groupableBy else groupableBy[0]

        return {
            'profile': get_current_profile(self.request),
            'locale': get_current_locale(self.request),
            'groupedBy': groupedBy,
            'groupableBy': groupableBy
        }