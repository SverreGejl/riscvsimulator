import atexit
import struct
import sys
import unittest
from collections import defaultdict
from pathlib import Path

TESTS_DIR = Path(__file__).parent / "tests"

outcomes = {}

def run_program(binPath):
    from everything import CPU

    cpu = CPU(str(binPath))
    cpu.start()
    return cpu

def read_expected(resPath):
    with open(resPath, "rb") as f:
        return list(struct.unpack("<32I", f.read()))


class ProgramTests(unittest.TestCase):
    def check_program(self, binPath):
        cpu = run_program(binPath)
        actual = [r % (1 << 32) for r in cpu.registers.registers]
        expected = read_expected(binPath.with_suffix(".res"))

        mismatches = [
            f"x{i}: expected 0x{e:08x}, got 0x{a:08x}"
            for i, (e, a) in enumerate(zip(expected, actual))
            if e != a
        ]
        self.assertFalse(mismatches, f"{binPath.name}:\n" + "\n".join(mismatches))


# ---------- report ----------

def short_reason(exc):
    if isinstance(exc, AssertionError):
        mismatches = [l for l in str(exc).splitlines() if l.startswith("x")]
        if mismatches:
            more = f" (+{len(mismatches) - 1} more)" if len(mismatches) > 1 else ""
            return f"{len(mismatches)} wrong register(s): {mismatches[0]}{more}"
        return str(exc).splitlines()[0]
    if isinstance(exc, SyntaxError):
        return f"SyntaxError in {Path(exc.filename).name} line {exc.lineno}: {exc.msg}"
    return f"{type(exc).__name__}: {exc}"


def record(key, status, reason=""):
    if not outcomes:
        atexit.register(print_report)
    outcomes[key] = (status, reason)


def natural(name):
    digits = "".join(c for c in name if c.isdigit())
    return (name.rstrip("0123456789"), int(digits) if digits else 0)


def print_report(out=None):
    out = out or sys.stderr
    byTask = defaultdict(list)
    for (task, name), (status, reason) in outcomes.items():
        byTask[task].append((name, status, reason))

    total = len(outcomes)
    passed = sum(1 for s, _ in outcomes.values() if s == "PASS")

    print("\n" + "=" * 60, file=out)
    print("RISC-V simulator test report", file=out)
    print("=" * 60, file=out)
    for task in sorted(byTask, key=natural):
        rows = sorted(byTask[task], key=lambda r: natural(r[0]))
        taskPassed = sum(1 for _, s, _ in rows if s == "PASS")
        print(f"\n{task.capitalize()}: {taskPassed}/{len(rows)} passed", file=out)
        for name, status, reason in rows:
            print(f"  [{status:5}] {name}" + (f" - {reason}" if reason else ""), file=out)
    print("\n" + "=" * 60, file=out)
    print(f"Total: {passed}/{total} passed, {total - passed} failing", file=out)


# ---------- one test per program ----------

def _make_test(binPath):
    key = (binPath.parent.name, binPath.stem)

    def test(self):
        try:
            self.check_program(binPath)
        except AssertionError as e:
            record(key, "FAIL", short_reason(e))
            raise
        except Exception as e:
            record(key, "ERROR", short_reason(e))
            raise
        record(key, "PASS")
    return test

for _bin in sorted(TESTS_DIR.glob("*/*.bin")):
    if _bin.with_suffix(".res").exists():
        setattr(ProgramTests, f"test_{_bin.parent.name}_{_bin.stem}", _make_test(_bin))

if __name__ == "__main__":
    unittest.main()
