import subprocess
import threading
import queue
import time
from pathlib import Path

class process:
    def __init__(self, path: str):
        self.path = path
        self.initialized = False
        self._queue = queue.Queue()
        self._thread = None

    def initialize(self):
        self.subsystem = subprocess.Popen(
            [self.path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            cwd=str(Path(self.path).parent)
        )
        self.initialized = True
        self._thread = threading.Thread(target=self._reader, daemon=True)
        self._thread.start()
        time.sleep(0.1)

    def _reader(self):
        for line in self.subsystem.stdout:
            parsed = self._parse_line(line.strip())
            if parsed:
                self._queue.put(parsed)

    def _parse_line(self, line: str) -> tuple | None:
        # Format: [handle:pid:addr:ctx:ctx2:name:hookcode:dll:function] text
        try:
            meta, _, text = line.partition("] ")
            fields = meta.lstrip("[").split(":")
            pid = int(fields[1], 16)
            hook = fields[6]
            return (pid, hook, text)
        except (IndexError, ValueError):
            return None

    def read(self):
        return self._queue.get()  # blocks until something arrives

    def attach(self, pid: int):
        self.subsystem.stdin.write(f"attach -P{pid}\n")
        self.subsystem.stdin.flush()

    def detach(self, pid: int):
        self.subsystem.stdin.write(f"detach -P{pid}\n")
        self.subsystem.stdin.flush()

    def hook(self, pid: int, hcode: str):
        self.subsystem.stdin.write(f"{hcode} -P{pid}\n")
        self.subsystem.stdin.flush()

    def terminate(self):
        self.subsystem.stdin.close()
        self.subsystem.terminate()