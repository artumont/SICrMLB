import logging
from PIL.Image import Image
import PIL.Image as PILImage

from sicrmlb.utils.device import _constants
from sicrmlb.utils.device.adb import AndroidDebugBridge
from sicrmlb.utils.device.decoder import Decoder

logger = logging.getLogger(__name__)

class Device:
    def __init__(self, device_id: str | None = None):
        self.device_id = device_id
        self.adb = AndroidDebugBridge()

    def __del__(self):
        self.stop_capture()

    def do_tap(self, x: int, y: int) -> None:
        """Simulate a tap on the Android device at the specified coordinates."""
        args = ["shell", "input", "tap", str(x), str(y)]
        self.adb._run_command(args)

    def start_capture(self) -> None:
        """Start capturing the screen of the Android device."""
        adb_pipe = self.adb.start_screenrecord(self.device_id).stdout
        if adb_pipe is None:
            raise RuntimeError("Failed to start screen recording via ADB.")
        self.decoder = Decoder(adb_pipe)

    def stop_capture(self) -> None:
        """Stop capturing the screen of the Android device."""
        if hasattr(self, "adb") and self.adb._process is not None:
            self.adb._process.terminate()
            self.adb._process = None
        if hasattr(self, "decoder"):
            self.decoder.frame_thread.join(timeout=1)

    def get_frame(self) -> Image:
        """Get the current frame from the Android device as a PIL Image."""
        frame = self.decoder.get_current_frame()
        if frame is None:
            raise RuntimeError("No frame available from decoder.")

        target_w = _constants.CAPTURE_WIDTH
        target_h = _constants.CAPTURE_HEIGHT

        if getattr(frame, "width", 0) >= target_w and getattr(frame, "height", 0) >= target_h:
            try:
                src_w = frame.width
                src_h = frame.height
                target_aspect = target_w / target_h
                src_aspect = src_w / src_h

                if src_aspect > target_aspect:
                    # source is wider -> crop width
                    crop_h = src_h
                    crop_w = int(target_aspect * crop_h)
                else:
                    # source is taller or equal -> crop height
                    crop_w = src_w
                    crop_h = int(crop_w / target_aspect)

                crop_x = (src_w - crop_w) // 2
                crop_y = (src_h - crop_h) // 2
                box = (crop_x, crop_y, crop_x + crop_w, crop_y + crop_h)

                pil = frame.to_image()
                center = pil.crop(box)
                if center.mode != "RGB":
                    center = center.convert("RGB")
                resized = center.resize((target_w, target_h), resample=PILImage.Resampling.LANCZOS)
                return resized
            except Exception:
                logger.warning("Failed to crop and resize frame, falling back to direct reformat.", exc_info=True)
                pass

        img = frame.reformat(
            width=target_w,
            height=target_h,
            format="rgb24",
        ).to_image()
        return img
