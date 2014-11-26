from lmkp.protocols.protocol import Protocol
from lmkp.views.views import (
    get_bbox_parameters,
    get_current_profile,
    get_current_logical_filter_operator,
    get_current_order_direction,
    get_current_involvement_details,
    get_current_limit,
    get_current_offset,
)


class StakeholderProtocol(Protocol):
    """
    TODO
    """

    def read_many(
            self, public_query=True, limit=None, offset=None, translate=True):
        """
        TODO
        """

        relevant_stakeholders = self.get_relevant_stakeholders_many(
            public_query=public_query)

        involvement_details = get_current_involvement_details(self.request)
        show_involvements = involvement_details != 'none'

        if limit is None:
            limit = get_current_limit(self.request)
        if offset is None:
            offset = get_current_offset(self.request)

        query, count = self.query_many(
            relevant_stakeholders, limit=limit, offset=offset,
            with_involvements=show_involvements)

        features = self.query_to_features(
            query, involvements=involvement_details, public_query=public_query,
            translate=translate)

        return {
            'total': count,
            'data': [f.to_json(self.request) for f in features]
        }

    def get_relevant_stakeholders_many(self, filter=None, public_query=False):
        pass

    def query_many(
            self, relevant_stakeholders, limit=None, offset=None,
            with_involvements=False, return_count=True,
            with_metadata=False):
        pass

    def query_to_features(
            self, query, involvements='none', public_query=False,
            translate=True):
        pass
