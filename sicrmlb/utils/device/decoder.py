import os
import threading
import time
from typing import IO
import av
import logging
import subprocess as sp

logger = logging.getLogger(__name__)


class Decoder:
    def __init__(self, adb_pipe: IO[bytes]):
        self.adb_pipe = adb_pipe
        self.codec = av.CodecContext.create("h264", "r")

        self._frame = None

    def get_current_frame(self) -> av.VideoFrame | None:
        """Get the current video frame from the decoder."""
        if self._frame is None:
            self._start_updating_frame()

        while self._frame is None:
            time.sleep(0.01)
            continue

        return self._frame

    def _start_updating_frame(self):
        self.frame_thread = threading.Thread(target=self._update_current_frame)
        self.frame_thread.daemon = True
        self.frame_thread.start()

    def _update_current_frame(self):
        if self.adb_pipe is None:
            raise RuntimeError("ADB pipe is not initialized.")

        for line in iter(self.adb_pipe.readline, b""):
            try:
                frame = self._get_last_frame(line)
                if frame is not None:
                    self._frame = frame
            except Exception as e:
                logger.error(f"Error decoding frame: {e}")

    def _get_last_frame(self, line: bytes) -> av.VideoFrame | None:
        if not line:
            return None

        if os.name == "nt":
            line = line.replace(b"\r\n", b"\n")

        packets = self.codec.parse(line)
        if not packets:
            return None

        frames = self.codec.decode(packets[-1])
        if not frames:
            return None
        return frames[-1]
