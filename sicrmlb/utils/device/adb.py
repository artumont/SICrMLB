import os
import pathlib
import re
import base64
from typing import IO
import subprocess as sp

from sicrmlb.utils.device._types import DeviceMetrics


class AndroidDebugBridge:
    def __init__(self):
        self._process = None
        self.binary = self._get_adb_path()
        
        self._ensure_daemon_running()

    def __del__(self):
        if self._process is not None:
            self._process.terminate()

    def start_screenrecord(self, device_id: str | None = None) -> sp.Popen:
        """Start the adb screenrecord process for the specified device."""
        device_metrics = self._get_device_metrics(device_id)
        args: list[str] = []
        if device_id:
            args += ["-s", device_id]
        cmd = (
            f"""#!/bin/bash
            while true; do
                screenrecord --output-format=h264 --time-limit "179" """
            f"""--size "{device_metrics.width}x{device_metrics.height}" --bit-rate "5M" -
            done\n"""
        )
        cmd = base64.b64encode(cmd.encode("utf-8")).decode("utf-8")
        cmd = ["echo", cmd, "|", "base64", "-d", "|", "sh"]
        cmd = " ".join(cmd) + "\n"
        args += ["shell", cmd]
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

    def _ensure_daemon_running(self) -> None:
        """Ensure that the adb daemon is running."""
        self._run_command(["start-server"])
    
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
