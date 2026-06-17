from arch import arch, detect_arch
from pathlib import Path
from process import process

BIN_DIR = Path(__file__).parent / "bin"

class textractor:
    def __init__(self):
        self.clis = {
            arch.x86: process(str(BIN_DIR / "x86" / "TextractorCLI.exe")),
            arch.x64: process(str(BIN_DIR / "x64" / "TextractorCLI.exe"))
        }
        self._pid_arch = {}     # pid -> arch
        self._filters = {}      # pid -> hcode | None

    def attach(self, pid: int, p_arch=arch.auto, hcode=None):
        if pid in self._pid_arch:
            return

        if p_arch == arch.auto:
            p_arch = detect_arch(pid)

        if not self.clis[p_arch].initialized:
            self.clis[p_arch].initialize()

        self.clis[p_arch].attach(pid)
        self._pid_arch[pid] = p_arch
        self._filters[pid] = hcode  # None means accept all hooks for this pid

        if hcode is not None:
            self.hook(pid=pid, hcode=hcode, p_arch=p_arch)

    def hook(self, pid: int, hcode: str, p_arch=arch.auto):
        if p_arch == arch.auto:
            p_arch = self._pid_arch.get(pid) or detect_arch(pid)
        self._filters[pid] = hcode
        self.clis[p_arch].hook(pid=pid, hcode=hcode)

    def detach(self, pid: int):
        p_arch = self._pid_arch.pop(pid, None)
        self._filters.pop(pid, None)
        if p_arch:
            self.clis[p_arch].detach(pid=pid)

    def listen(self, pid: int):
        if pid not in self._pid_arch:
            raise RuntimeError(f"PID {pid} is not attached. Call attach() first.")

        p_arch = self._pid_arch[pid]
        cli = self.clis[p_arch]

        while True:
            out_pid, hook, text = cli.read()

            if out_pid != pid:
                continue

            hcode_filter = self._filters.get(pid)
            if hcode_filter is not None and hook != hcode_filter:
                continue

            if not text:
                continue

            yield (pid, hook, text)