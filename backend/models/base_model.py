from abc import ABC, abstractmethod
from typing import Any


class BaseModel(ABC):
    @abstractmethod
    def fit(self, frame: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    def predict(self, horizon: int, history_frame: Any) -> list[float]:
        raise NotImplementedError

    def get_feature_importance(self) -> dict[str, float]:
        return {}
