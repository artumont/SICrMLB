from PIL import Image

from sicrmlb.utils.device import _constants
from sicrmlb.utils.device.adb import AndroidDebugBridge
from sicrmlb.utils.device.decoder import Decoder


class VideoCapture:
    def __init__(self):
        self.adb = AndroidDebugBridge()

    def __del__(self):
        self.stop_capture()
    
    def start_capture(self, device_id: str | None = None) -> None:
        adb_pipe = self.adb.start_screenrecord(device_id).stdout
        if adb_pipe is None:
            raise RuntimeError("Failed to start screen recording via ADB.")
        self.decoder = Decoder(adb_pipe)
    
    def stop_capture(self) -> None:
        if hasattr(self, "adb") and self.adb._process is not None:
            self.adb._process.terminate()
            self.adb._process = None
        
    def get_frame(self) -> Image.Image:
        frame = self.decoder.get_current_frame()
        if frame is None:
            raise RuntimeError("No frame available from decoder.")
        img = frame.reformat(width=_constants.CAPTURE_WIDTH, height=_constants.CAPTURE_HEIGHT, format="rgb24").to_image()
        return img
