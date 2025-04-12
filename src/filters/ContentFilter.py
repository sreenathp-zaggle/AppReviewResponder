from abc import ABC, abstractmethod

class ContentFilter(ABC):
    @abstractmethod
    def check(self, review_text: str) -> bool:
        pass

    @abstractmethod
    def reason(self) -> str:
        pass