import logging
import numpy as np
from typing import Any
from PIL.Image import Image
from sicrmlb.gamestate._base import BaseDetector
from sicrmlb.gamestate._types import RGBColor, RGBRange
from sicrmlb.gamestate.elixir._types import ElixirState
from sicrmlb.utils.device._constants import CAPTURE_HEIGHT, CAPTURE_WIDTH
from sicrmlb.gamestate.elixir._constants import (
    CROPPED_ELIXIR_HEIGHT,
    CROPPED_ELIXIR_WIDTH,
    ELIXIR_COUNT,
    ELIXIR_START_X,
    ELIXIR_START_Y,
    ELIXIR_UNIT_HEIGHT,
    ELIXIR_UNIT_WIDTH,
)

logger = logging.getLogger(__name__)


class ElixirDetector(BaseDetector):
    def __init__(self):
        self.analysis_y_offset = 3
        self.initial_x_offset = 13
        self.elixir_color_range = RGBRange(
            lower=RGBColor(r=190, g=10, b=190),
            upper=RGBColor(r=255, g=120, b=255),
        )

    def perform_analysis(self, frame: Image) -> ElixirState:
        cropped_frame = self._ensure_cropped(frame).convert("RGB")

        offset = 0
        elixir_points = []
        for i in range(ELIXIR_COUNT):
            point_x = offset + (ELIXIR_UNIT_WIDTH // 2)
            point_x += self.initial_x_offset if i == 0 else 0
            point_y = (ELIXIR_UNIT_HEIGHT // 2) + self.analysis_y_offset
            offset += ELIXIR_UNIT_WIDTH
            elixir_points.append((point_x, point_y))
        elixir_points.reverse()  # Go from highest to lowest

        elixir_amount = 10
        for point in elixir_points:
            raw_pixel = self._ensure_tuple_pixel(cropped_frame.getpixel(point))
            if raw_pixel is None:
                continue
            pixel = RGBColor.pixel_to_color(raw_pixel)
            if not self._is_color_in_range(pixel, self.elixir_color_range):
                elixir_amount -= 1
            else:
                break  # Found elixir, stop checking further

        return ElixirState(
            elixir_amount=elixir_amount,
            elixir_percentage=elixir_amount / ELIXIR_COUNT,
            is_elixir_full=(elixir_amount == ELIXIR_COUNT),
        )

    @staticmethod
    def _ensure_cropped(frame: Image) -> Image:
        if frame.height != CROPPED_ELIXIR_HEIGHT or frame.width != CROPPED_ELIXIR_WIDTH:
            logger.warning(
                f"Expected frame size of {CROPPED_ELIXIR_WIDTH}x{CROPPED_ELIXIR_HEIGHT}, "
                f"but got {frame.width}x{frame.height}."
            )
            logger.info("Cropping frame to elixir bar dimensions.")

            if frame.width != CAPTURE_WIDTH or frame.height != CAPTURE_HEIGHT:
                logger.error("Frame size does not match capture dimensions.")
                raise ValueError("Invalid frame size for elixir detection.")

            frame = frame.crop(
                (
                    ELIXIR_START_X,
                    ELIXIR_START_Y,
                    ELIXIR_START_X + CROPPED_ELIXIR_WIDTH,
                    ELIXIR_START_Y + CROPPED_ELIXIR_HEIGHT,
                )
            )
            logger.info("Frame cropped to elixir bar dimensions.")

        return frame

    @staticmethod
    def _ensure_tuple_pixel(pixel: Any) -> tuple[int, int, int] | None:
        if isinstance(pixel, tuple) and len(pixel) == 3:
            return pixel
        raise ValueError("Pixel is not a valid RGB tuple.")

    @staticmethod
    def _is_color_in_range(pixel: RGBColor, color_range: RGBRange) -> bool:
        return (
            color_range.lower.r <= pixel.r <= color_range.upper.r
            and color_range.lower.g <= pixel.g <= color_range.upper.g
            and color_range.lower.b <= pixel.b <= color_range.upper.b
        )
