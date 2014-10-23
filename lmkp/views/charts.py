from pyramid.httpexceptions import HTTPNotFound
from pyramid.renderers import render_to_response
from pyramid.view import view_config

from lmkp.custom import get_customized_template_path
from lmkp.views.views import BaseView


class ChartsView(BaseView):

    @view_config(route_name='charts_overview')
    def charts_overview(self):

        return render_to_response(
            get_customized_template_path(self.request, 'charts_view.mak'),
            self.get_base_template_values(), self.request)

    @view_config(route_name='charts')
    @view_config(route_name='charts_no_slash')
    def charts(self):

        chart_type = self.request.matchdict.get('type', 'bars')
        if chart_type == 'bars':
            params = self.request.matchdict.get('params')
            if params == ('sh',):
                template = 'barchart_sh'
            else:
                template = 'barchart_a'
        else:
            return HTTPNotFound()

        attr = self.request.params.get('attr', 0)

        template_values = self.template_values
        template_values.update({
            'attr': attr
        })

        return render_to_response(
            get_customized_template_path(
                self.request, 'charts/%s.mak' % template),
            template_values, self.request)
