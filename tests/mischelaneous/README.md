# Miscellaneous tests

Extra RV32I test programs (`.s` source, `.bin` program, `.res` expected registers)
collected from other DTU 02155 RISC-V simulator repositories on GitHub.
Only tests using the RV32I base instructions are included (no mul/div/rem).

| Test | Source |
|------|--------|
| addlarge_old, addneg_old, addpos_old, shift_old, branchcnt_old, branchmany_old | https://github.com/TheAIBot/RISC-V_Sim (older course version, exits with `a0 = 10`) |
| test_ecall | https://github.com/TheAIBot/RISC-V_Sim (only `ecall` with `a0 = 10` ends the program) |
| t14_old | https://github.com/andersthuesen/rv32i-simulator (older version of task4/t14) |
