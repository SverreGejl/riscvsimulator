lui t0 0x100      # t0 = 0x100000, first address past the 1 MB memory
lw t1 0(t0)       # must raise: read out of range
addi a7 x0 10
ecall
