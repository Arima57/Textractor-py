# textractor.py
from arch import arch, detect_arch
from pathlib import Path
from process import process

BIN_DIR = Path(__file__).parent / "bin"

class textractor:
    def __init__(self):
        self.x86_path = str(BIN_DIR / "x86" / "TextractorCLI.exe")
        self.x64_path = str(BIN_DIR / "x64" / "TextractorCLI.exe")

        self.clis = {
            arch.x86: process(self.x86_path),
            arch.x64: process(self.x64_path)
        }
        self._pid_arch = {} 

    def attach(self, pid: int, p_arch=arch.auto, hcode=None):
        if pid in self._pid_arch:
            return 

        if p_arch == arch.auto:
            p_arch = detect_arch(pid)

        if not self.clis[p_arch].initialized:
            self.clis[p_arch].initialize()

        self.clis[p_arch].attach(pid)
        self._pid_arch[pid] = p_arch

        if hcode is not None:
            self.hook(pid=pid, hcode=hcode, p_arch=p_arch)

    def hook(self, pid: int, hcode: str, p_arch=arch.auto):
        if p_arch == arch.auto:
            p_arch = self._pid_arch.get(pid) or detect_arch(pid)
        self.clis[p_arch].hook(pid=pid, hcode=hcode)

    def detach(self, pid: int):
        p_arch = self._pid_arch.pop(pid, None)
        if p_arch:
            self.clis[p_arch].detach(pid=pid)

    def listen(self, pid: int):
        p_arch = self._pid_arch.get(pid)
        if p_arch is None:
            raise RuntimeError(f"PID {pid} is not attached. Call attach() first.")
        q = self.clis[p_arch].get_queue(pid)
        while True:
            yield q.get() 