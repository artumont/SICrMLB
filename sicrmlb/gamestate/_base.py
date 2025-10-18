import av
from pydantic import BaseModel


class BaseState(BaseModel):
    timestamp: float


class BaseDetector:
    def perform_analysis(self, frame: av.VideoFrame) -> BaseState:
        raise NotImplementedError("Subclasses should implement this method")
