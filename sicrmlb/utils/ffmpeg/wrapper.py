import os
import pathlib
import subprocess as sp

class FFmpeg:
    def __init__(self):
        self.binary = self.get_ffmpeg_path()
    
    @staticmethod
    def get_ffmpeg_path() -> pathlib.Path:
        ffmpeg_path = pathlib.Path(os.getcwd(), "bin", "ffmpeg")
        if ffmpeg_path.exists():
            return ffmpeg_path