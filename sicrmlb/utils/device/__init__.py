from PIL.Image import Image

from sicrmlb.utils.device import _constants
from sicrmlb.utils.device.adb import AndroidDebugBridge
from sicrmlb.utils.device.decoder import Decoder


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
        img = frame.reformat(
            width=_constants.CAPTURE_WIDTH,
            height=_constants.CAPTURE_HEIGHT,
            format="rgb24",
        ).to_image()
        return img
