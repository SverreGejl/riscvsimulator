lui t0 0x100      # t0 = 0x100000, first address past the 1 MB memory
sw x0 0(t0)       # must raise: write out of range
addi a7 x0 10
ecall
