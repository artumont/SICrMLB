from PIL.Image import Image
from datetime import datetime
from pydantic import BaseModel


class BaseState(BaseModel):
    timestamp: float = datetime.now().timestamp()


class BaseDetector:
    def perform_analysis(self, frame: Image) -> BaseState:
        raise NotImplementedError("Subclasses should implement this method")
