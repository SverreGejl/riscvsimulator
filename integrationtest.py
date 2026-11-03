import contextlib
import io
import struct
import unittest

from everything import CPU


class IntegrationTest(unittest.TestCase):
    def test_addlarge(self):
        cpu = CPU("tests/task1/addlarge.bin")
        cpu.start()

        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            cpu.printRegisters()

        # .res is the 32 registers as little-endian signed 32-bit ints
        with open("tests/task1/addlarge.res", "rb") as f:
            expected = struct.unpack("<32i", f.read())
        expectedOutput = "".join(f"{i} {val}\n" for i, val in enumerate(expected))

        self.assertEqual(out.getvalue(), expectedOutput)

    def test_addlarge_stops_at_ecall(self):
        cpu = CPU("tests/task1/addlarge.bin")
        cpu.start()
        self.assertEqual(cpu.pc, 0x18)


if __name__ == "__main__":
    unittest.main()
