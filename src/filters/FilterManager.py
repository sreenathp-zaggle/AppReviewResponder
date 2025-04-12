from filters.ContentFilter import ContentFilter


class FilterManager:
    def __init__(self, filters: list[ContentFilter]):
        self.filters = filters

    def apply_filters(self, review_text: str):
        for filter in self.filters:
            if filter.check(review_text):
                return True, filter.reason(), filter.generate_response_based_on_confidence()
        return False, None, None
