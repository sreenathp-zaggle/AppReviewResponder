from abc import ABC, abstractmethod

class ContentFilter(ABC):
    @abstractmethod
    def check(self, review_text: str) -> bool:
        pass

    @abstractmethod
    def reason(self) -> str:
        pass

    @abstractmethod
    def generate_response_based_on_confidence(self):
        pass