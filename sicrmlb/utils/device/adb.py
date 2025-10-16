import os
import pathlib
import re
from typing import IO
import subprocess as sp

from sicrmlb.utils.device._types import DeviceMetrics


class AndroidDebugBridge:
    def __init__(self):
        self._process = None
        self.binary = self._get_adb_path()

    def __del__(self):
        if self._process is not None:
            self._process.terminate()

    def start_screenrecord(self, device_id: str | None = None) -> sp.Popen:
        args: list[str] = []
        if device_id:
            args += ["-s", device_id]
        args += ["shell", "screenrecord", "--output-format=h264", "-"]
        return self._open_process(args)

    def _run_command(self, args: list[str]) -> sp.CompletedProcess:
        cmd = [str(self.binary)] + args
        return sp.run(
            cmd,
            capture_output=True,
            check=True,
            text=True,
        )

    def _open_process(
        self, args: list[str], stdin_pipe: IO[bytes] | None = None
    ) -> sp.Popen:
        if self._process is not None:
            self._process.terminate()

        cmd = [str(self.binary)] + args

        if stdin_pipe is not None:
            return sp.Popen(cmd, stdin=stdin_pipe, stdout=sp.PIPE)

        self._process = sp.Popen(cmd, stdout=sp.PIPE)
        return self._process

    def _get_device_metrics(self, device_id: str | None = None) -> DeviceMetrics:
        cmd = [str(self.binary)]
        if device_id:
            cmd += ["-s", device_id]
        cmd += ["shell", "wm", "size"]
        proc = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE, text=True, shell=False)
        out = (proc.stdout or "").strip()

        if proc.returncode != 0:
            stderr = (proc.stderr or "").strip()
            raise RuntimeError(
                f"adb command failed (rc={proc.returncode}). stderr: {stderr!r}"
            )

        m = re.search(r"(\d+)x(\d+)", out)
        if not m:
            raise RuntimeError(f"Could not parse device size from: {out!r}")
        return DeviceMetrics(width=int(m[1]), height=int(m[2]))

    @staticmethod
    def _get_adb_path() -> pathlib.Path | None:
        candidates = [
            pathlib.Path(os.getcwd(), "bin", "adb.exe"),
            pathlib.Path(os.getcwd(), "bin", "adb"),
        ]
        for path in candidates:
            if path.exists():
                return path
        raise FileNotFoundError("adb not found in bin/ or PATH")
