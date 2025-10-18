import pytest
from PIL.Image import Image
from PIL import Image as PILImage, ImageDraw
from pathlib import Path

from sicrmlb.gamestate.elixir._types import ElixirState
from sicrmlb.gamestate.elixir.detector import ElixirDetector
from sicrmlb.gamestate._types import RGBColor
from sicrmlb.gamestate.elixir._constants import (
    ELIXIR_COUNT,
    ELIXIR_UNIT_WIDTH,
    ELIXIR_UNIT_HEIGHT,
)


@pytest.fixture
def sample_frame_full_elixir() -> Image:
    """Fixture to load a test screenshot image named 'testing_frame.png' located next to this test file."""
    img_path = Path(__file__).with_name("testing_frame.png")
    return PILImage.open(img_path)


@pytest.mark.elixir
def test_elixir_detector_full_elixir(sample_frame_full_elixir: Image):
    detector = ElixirDetector()
    elixir_state = detector.perform_analysis(sample_frame_full_elixir)

    expected = 10
    if elixir_state.elixir_amount != expected:
        cropped = ElixirDetector._ensure_cropped(sample_frame_full_elixir).convert("RGB")
        draw = ImageDraw.Draw(cropped)
        # recreate the points the detector checks (same logic as detector)
        offset = 0
        elixir_points = []
        for i in range(ELIXIR_COUNT):
            point_x = offset + (ELIXIR_UNIT_WIDTH // 2)
            point_x += detector.initial_x_offset if i == 0 else 0
            point_y = (ELIXIR_UNIT_HEIGHT // 2) + detector.analysis_y_offset
            offset += ELIXIR_UNIT_WIDTH
            elixir_points.append((point_x, point_y))
        elixir_points.reverse()  # detector checks from highest to lowest
        # draw markers: green if detected as elixir, red otherwise
        radius = 1
        for pt in elixir_points:
            raw_pixel = cropped.getpixel(pt)
            # normalize pixel to 3-tuple
            r, g, b = int(raw_pixel[0]), int(raw_pixel[1]), int(raw_pixel[2])  # type: ignore
            color_obj = RGBColor.pixel_to_color((r, g, b))
            in_range = detector._is_color_in_range(color_obj, detector.elixir_color_range)
            fill = "lime" if in_range else "red"
            draw.ellipse(
                (pt[0] - radius, pt[1] - radius, pt[0] + radius, pt[1] + radius),
                outline="yellow",
                fill=fill,
            )
        out_file = Path(__file__).with_name("debug_cropped_elixir_with_points.png")
        cropped.save(out_file)

    assert isinstance(elixir_state, ElixirState)
    assert elixir_state.elixir_amount == expected
    assert elixir_state.elixir_percentage == expected / elixir_state.max_elixir
    assert elixir_state.is_elixir_full is (elixir_state.elixir_amount == elixir_state.max_elixir)
