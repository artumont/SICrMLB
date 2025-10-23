from PIL.Image import Image
from sicrmlb.gamestate._base import BaseDetector, BaseState


class DeckDetector(BaseDetector):
    def __init__(self):
        pass

    def perform_analysis(self, frame: Image) -> BaseState:
        raise NotImplementedError("Deck detection not yet implemented")
