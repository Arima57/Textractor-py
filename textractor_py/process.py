# process.py
import subprocess
import threading
import queue
import time

class process:
    def __init__(self, path: str):
        self.path = path
        self.initialized = False
        self._queues = {}       
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
            cwd=str(__import__("pathlib").Path(self.path).parent)
        )
        self.initialized = True
        self._thread = threading.Thread(target=self._reader, daemon=True)
        self._thread.start()
        time.sleep(0.1)

    def _reader(self):
        buffer = []
        for line in self.subsystem.stdout:
            stripped = line.strip()
            if stripped == "":
                if buffer:
                    chunk = "\n".join(buffer)
                    pid = self._parse_pid(chunk)
                    if pid and pid in self._queues:
                        self._queues[pid].put(chunk)
                    buffer = []
            else:
                buffer.append(stripped)

    def _parse_pid(self, chunk: str) -> int | None:
        # chunk first line format: handle|pid|addr|ctx|ctx2|name|code:text
        try:
            first_line = chunk.split("\n")[0]
            parts = first_line.split("|")
            return int(parts[1], 16)  # pid is second field, hex
        except (IndexError, ValueError):
            return None

    def register_pid(self, pid: int):
        if pid not in self._queues:
            self._queues[pid] = queue.Queue()

    def unregister_pid(self, pid: int):
        self._queues.pop(pid, None)

    def attach(self, pid: int):
        self.register_pid(pid)
        self.subsystem.stdin.write(f"attach -P{pid}\n")
        self.subsystem.stdin.flush()

    def detach(self, pid: int):
        self.subsystem.stdin.write(f"detach -P{pid}\n")
        self.subsystem.stdin.flush()
        self.unregister_pid(pid)

    def hook(self, pid: int, hcode: str):
        self.subsystem.stdin.write(f"{hcode}")
        self.subsystem.stdin.flush()

    def get_queue(self, pid: int) -> queue.Queue:
        return self._queues[pid]

    def terminate(self):
        self.subsystem.stdin.close()
        self.subsystem.terminate()