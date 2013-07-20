from pyramid.view import view_config

from lmkp.views.views import BaseView
from lmkp.views.profile import get_current_profile
from lmkp.views.profile import get_current_locale

class ChartsView(BaseView):

    @view_config(route_name='charts_overview', renderer='lmkp:templates/charts/overview.mak')
    def charts_overview(self):

        self._handle_parameters()

        return {'profile': get_current_profile(self.request), 'locale': get_current_locale(self.request)}