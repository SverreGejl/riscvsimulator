import sys

from everything import CPU

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: python run.py <path/to/program.bin>")
    cpu = CPU(sys.argv[1])
    cpu.start()
    cpu.printRegisters()
