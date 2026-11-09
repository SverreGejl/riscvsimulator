# Instruction formats from the RV32I base instruction set table
def signExtend(val, bits):
    return val - (1 << bits) if val & (1 << (bits - 1)) else val

def bits(word, hi, lo):
    return (word >> lo) & ((1 << (hi - lo + 1)) - 1)

class RType:
    def __init__(self, word):
        self.opcode = bits(word, 6, 0)
        self.rd = bits(word, 11, 7)
        self.funct3 = bits(word, 14, 12)
        self.rs1 = bits(word, 19, 15)
        self.rs2 = bits(word, 24, 20)
        self.funct7 = bits(word, 31, 25)

class IType:
    def __init__(self, word):
        self.opcode = bits(word, 6, 0)
        self.rd = bits(word, 11, 7)
        self.funct3 = bits(word, 14, 12)
        self.rs1 = bits(word, 19, 15)
        self.imm = signExtend(bits(word, 31, 20), 12)

class SType:
    def __init__(self, word):
        self.opcode = bits(word, 6, 0)
        self.funct3 = bits(word, 14, 12)
        self.rs1 = bits(word, 19, 15)
        self.rs2 = bits(word, 24, 20)
        self.imm = signExtend(bits(word, 31, 25) << 5 | bits(word, 11, 7), 12)

class SBType:
    def __init__(self, word):
        self.opcode = bits(word, 6, 0)
        self.funct3 = bits(word, 14, 12)
        self.rs1 = bits(word, 19, 15)
        self.rs2 = bits(word, 24, 20)
        imm = (bits(word, 31, 31) << 12 | bits(word, 7, 7) << 11
               | bits(word, 30, 25) << 5 | bits(word, 11, 8) << 1)
        self.imm = signExtend(imm, 13)

class UType:
    def __init__(self, word):
        self.opcode = bits(word, 6, 0)
        self.rd = bits(word, 11, 7)
        self.imm = signExtend(bits(word, 31, 12) << 12, 32)

class UJType:
    def __init__(self, word):
        self.opcode = bits(word, 6, 0)
        self.rd = bits(word, 11, 7)
        imm = (bits(word, 31, 31) << 20 | bits(word, 19, 12) << 12
               | bits(word, 20, 20) << 11 | bits(word, 30, 21) << 1)
        self.imm = signExtend(imm, 21)

typeByOpcode = {
    0b0110011: RType,   # ADD, SUB, ...
    0b0010011: IType,   # ADDI, SLLI, ...
    0b0000011: IType,   # LB, LW, ...
    0b1100111: IType,   # JALR
    0b1110011: IType,   # ECALL/SCALL, ...
    0b0001111: IType,   # FENCE
    0b0100011: SType,   # SB, SH, SW
    0b1100011: SBType,  # BEQ, BNE, ...
    0b0110111: UType,   # LUI
    0b0010111: UType,   # AUIPC
    0b1101111: UJType,  # JAL
}
