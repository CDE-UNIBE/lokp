import csv

import io


class JavaScriptRenderer(object):
    def __call__(self, info):

        def _render(value, system):

            # Get the request and set the response content type to JSON
            request = system.get('request')
            if request is not None:
                response = request.response
                response.content_type = 'application/javascript'

            return value

        return _render


class CSVRenderer(object):
    def __call__(self, info):

        def _render(value, system):

            fout = io.StringIO()
            writer = csv.writer(fout, delimiter=';', quoting=csv.QUOTE_ALL)
            writer.writerow(value['header'])
            writer.writerows(value['rows'])

            resp = system['request'].response
            resp.content_type = 'text/csv'
            resp.content_disposition = 'attachment;filename="report.csv"'
            return fout.getvalue()

        return _render
