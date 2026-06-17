from .arch import arch, detect_arch
from pathlib import Path
from .process import process

BIN_DIR = Path(__file__).parent / "bin"

class textractor:
    def __init__(self):
        self.clis = {
            arch.x86: process(str(BIN_DIR / "x86" / "TextractorCLI.exe")),
            arch.x64: process(str(BIN_DIR / "x64" / "TextractorCLI.exe"))
        }
        self._pid_arch = {}     # pid -> arch

    def attach(self, pid: int, p_arch=arch.auto):
        if pid in self._pid_arch:
            return

        if p_arch == arch.auto:
            p_arch = detect_arch(pid)

        if not self.clis[p_arch].initialized:
            self.clis[p_arch].initialize()

        self.clis[p_arch].attach(pid)
        self._pid_arch[pid] = p_arch

    def detach(self, pid: int):
        p_arch = self._pid_arch.pop(pid, None)
        if p_arch:
            self.clis[p_arch].detach(pid=pid)

    def listen(self, hook:None, pid:int=0):
        if pid!=0 and pid not in self._pid_arch:
            raise RuntimeError(f"PID {pid} is not attached. Call attach() first.")

        p_arch = self._pid_arch[pid]
        cli = self.clis[p_arch]

        while True:
            out_pid, out_hook, text = cli.read()

            if pid == 0 and hook == None:
                yield (out_pid, out_hook, text)
            elif (pid != 0 and pid == out_pid) or (hook is not None and hook == out_hook):
                """It might cause an error if an app unintentionally happens to have the intended hook
                but that would be insane and I'd like to see it happen"""
                if (pid != 0 and pid != out_pid) and hook == out_hook:
                    continue #i'd like to let it go but like.....
                if (hook is not None and hook != out_hook):
                    continue
                yield (out_pid, out_hook, text)