from instructionType import typeByOpcode, RType, IType, SType, SBType, UType, UJType

regSize = 1<<32
adressSize = 1<<8

def signed(val, bits):
    return (val & ((1 << (bits - 1))-1)) - (val&(1<<(bits-1)))

def signExtend(val, bit, length):
    if val&(1<<(bit-1)): #Negative
        return val | ((1<<(length-bit))-1)<<bit
    else:
        return val

class importCode:
    def __init__(self,path):
        self.path = path

    def extractCode(self):
        instructions = []

        # Read binary file bite wise
        with open(self.path,'rb') as f:
            data = f.read()

        # 32bit = 4 Byte: select 4 bytes at a time
        for i in range(0, len(data), 4):
            chunk = data[i:i+4] # 4 bytes at a time 
            word = int.from_bytes(chunk, byteorder='little') #little-endian machine
            instructions.append(word) 
        return instructions

class memory:
    def __init__(self,size):
        self.size = size
        self.memory = [0 for i in range(self.size)]

    def getAdress(self,address):
        return self.memory[address] % adressSize

    def setAdress(self,address, val):
        self.memory[address] = val % adressSize

    def getSize(self):
        return self.size

class registerFile:
    def __init__(self):
        self.registers = [0 for i in range(32)]

    def setRegister(self,idx,val):
        if (idx>0): #Don't overwrite the x0 register
            self.registers[idx] = val

    def getRegister(self,idx):
        return self.registers[idx]

    def printRegisters(self):
        print("Registers: ")
        for i in range(32):
            print(i, self.registers[i])

#Everything was implemented following this overview here: https://lhtin.github.io/01world/app/riscv-isa/?xlen=32
class codeExecuter:
    def executeInstruction(self, instruction: typeByOpcode, cpu):
        match instruction:
            #End of program
            case IType(opcode=0b1110011, funct3=0b000, imm=0):  # ECALL
                if cpu.getRegister(10) == 10 or cpu.getRegister(17) == 10: #a0 == 10 or a7 == 10
                    return True #Just end program
                else:
                    cpu.setPC(cpu.getPC() + 4)
                    return False

            #Upper instructions
            case UType(opcode=0b0110111): #LUI
                cpu.setRegister(instruction.rd, instruction.imm<<12)
                cpu.setPC(cpu.getPC() + 4)
                return False
            case UType(opcode=0b0010111): #AUIPC
                cpu.setRegister(instruction.rd, (instruction.imm<<12)+cpu.getPC())
                cpu.setPC(cpu.getPC() + 4)
                return False

            #Jumps
            case UJType(opcode=0b1101111): #JAL
                targetPC = signExtend(instruction.imm<<1, 21, 32) + cpu.getPC()
                cpu.setRegister(instruction.rd, cpu.getPC() + 4)
                cpu.setPC(targetPC) #It sets the pc in offsets of 2 bytes, hence << 1
                return False
            case IType(opcode=0b1100111, funct3=0b000): #JALR
                targetPC = (signExtend(instruction.imm, 12, 32) + cpu.getRegister(instruction.rs1)) & ~1
                cpu.setRegister(instruction.rd, cpu.getPC() + 4)
                cpu.setPC(targetPC)
                return False

            #Branches
            case SBType(opcode=0b1100011, funct3=0b000): #BEQ
                cpu.setPC(cpu.getPC() + (signExtend(instruction.imm<<1, 13, 32)) if cpu.getRegister(instruction.rs1) == cpu.getRegister(instruction.rs2) else cpu.getPC() + 4)
                return False
            case SBType(opcode=0b1100011, funct3=0b001): #BNE
                cpu.setPC(cpu.getPC() + (signExtend(instruction.imm<<1, 13, 32)) if cpu.getRegister(instruction.rs1) != cpu.getRegister(instruction.rs2) else cpu.getPC() + 4)
                return False
            case SBType(opcode=0b1100011, funct3=0b100): #BLT
                cpu.setPC(cpu.getPC() + (signExtend(instruction.imm<<1, 13, 32)) if signed(cpu.getRegister(instruction.rs1), 32) < signed(cpu.getRegister(instruction.rs2), 32) else cpu.getPC() + 4)
                return False
            case SBType(opcode=0b1100011, funct3=0b110): #BLTU
                cpu.setPC(cpu.getPC() + (signExtend(instruction.imm<<1, 13, 32)) if cpu.getRegister(instruction.rs1) < cpu.getRegister(instruction.rs2) else cpu.getPC() + 4)
                return False
            case SBType(opcode=0b1100011, funct3=0b101): #BGE
                cpu.setPC(cpu.getPC() + (signExtend(instruction.imm<<1, 13, 32)) if signed(cpu.getRegister(instruction.rs1), 32) >= signed(cpu.getRegister(instruction.rs2), 32) else cpu.getPC() + 4)
                return False
            case SBType(opcode=0b1100011, funct3=0b111): #BGEU
                cpu.setPC(cpu.getPC() + (signExtend(instruction.imm<<1, 13, 32)) if cpu.getRegister(instruction.rs1) >= cpu.getRegister(instruction.rs2) else cpu.getPC() + 4)
                return False

            #Loads
            case IType(opcode=0b0000011, funct3=0b000): #LB
                cpu.setRegister(instruction.rd, signExtend(cpu.getMemory(cpu.getRegister(instruction.rs1) + signExtend(instruction.imm, 12, 32),1), 8,32))
                cpu.setPC(cpu.getPC() + 4)
                return False
            case IType(opcode=0b0000011, funct3=0b001): #LH
                cpu.setRegister(instruction.rd, signExtend(cpu.getMemory(cpu.getRegister(instruction.rs1) + signExtend(instruction.imm, 12, 32),2), 16,32))
                cpu.setPC(cpu.getPC() + 4)
                return False
            case IType(opcode=0b0000011, funct3=0b010): #LW
                cpu.setRegister(instruction.rd, cpu.getMemory(cpu.getRegister(instruction.rs1) + signExtend(instruction.imm, 12, 32),4))
                cpu.setPC(cpu.getPC() + 4)
                return False
            case IType(opcode=0b0000011, funct3=0b100): #LBU
                cpu.setRegister(instruction.rd, cpu.getMemory(cpu.getRegister(instruction.rs1) + signExtend(instruction.imm, 12, 32),1))
                cpu.setPC(cpu.getPC() + 4)
                return False
            case IType(opcode=0b0000011, funct3=0b101): #LHU
                cpu.setRegister(instruction.rd, cpu.getMemory(cpu.getRegister(instruction.rs1) + signExtend(instruction.imm, 12, 32),2))
                cpu.setPC(cpu.getPC() + 4)
                return False

            #Stores
            case SType(opcode=0b0100011, funct3=0b000): #SB
                cpu.setMemory(cpu.getRegister(instruction.rs1) + signExtend(instruction.imm, 12, 32), cpu.getRegister(instruction.rs2), 1)
                cpu.setPC(cpu.getPC() + 4)
                return False
            case SType(opcode=0b0100011, funct3=0b001): #SH
                cpu.setMemory(cpu.getRegister(instruction.rs1) + signExtend(instruction.imm, 12, 32), cpu.getRegister(instruction.rs2), 2)
                cpu.setPC(cpu.getPC() + 4)
                return False
            case SType(opcode=0b0100011, funct3=0b010): #SW
                cpu.setMemory(cpu.getRegister(instruction.rs1) + signExtend(instruction.imm, 12, 32), cpu.getRegister(instruction.rs2), 4)
                cpu.setPC(cpu.getPC() + 4)
                return False

            #Immediates
            case IType(opcode=0b0010011, funct3=0b000): #ADDI
                cpu.setRegister(instruction.rd, cpu.getRegister(instruction.rs1) + signExtend(instruction.imm,12,32))
                cpu.setPC(cpu.getPC() + 4)
                return False
            case IType(opcode=0b0010011, funct3=0b010): #SLTI
                cpu.setRegister(instruction.rd, 1 if signed(cpu.getRegister(instruction.rs1),32) < signed(signExtend(instruction.imm, 12, 32),32) else 0)
                cpu.setPC(cpu.getPC() + 4)
                return False
            case IType(opcode=0b0010011, funct3=0b011): #SLTIU
                cpu.setRegister(instruction.rd, 1 if cpu.getRegister(instruction.rs1) < signExtend(instruction.imm, 12, 32) else 0)
                cpu.setPC(cpu.getPC() + 4)
                return False
            case IType(opcode=0b0010011, funct3=0b100): #XORI
                cpu.setRegister(instruction.rd, cpu.getRegister(instruction.rs1) ^ signExtend(instruction.imm,12,32))
                cpu.setPC(cpu.getPC() + 4)
                return False
            case IType(opcode=0b0010011, funct3=0b110): #ORI
                cpu.setRegister(instruction.rd, cpu.getRegister(instruction.rs1) | signExtend(instruction.imm, 12, 32))
                cpu.setPC(cpu.getPC() + 4)
                return False
            case IType(opcode=0b0010011, funct3=0b111): #ANDI
                cpu.setRegister(instruction.rd, cpu.getRegister(instruction.rs1) & signExtend(instruction.imm, 12, 32))
                cpu.setPC(cpu.getPC() + 4)
                return False
            case IType(opcode=0b0010011, funct3=0b001): #SLLI
                cpu.setRegister(instruction.rd, cpu.getRegister(instruction.rs1) << (instruction.imm%32))
                cpu.setPC(cpu.getPC() + 4)
                return False
            case IType(opcode=0b0010011, funct3=0b101) if (instruction.imm >> 5) == 0b0000000: #SRLI
                cpu.setRegister(instruction.rd, cpu.getRegister(instruction.rs1) >> (instruction.imm%32))
                cpu.setPC(cpu.getPC() + 4)
                return False
            case IType(opcode=0b0010011, funct3=0b101) if (instruction.imm >> 5) == 0b0100000: #SRAI
                cpu.setRegister(instruction.rd, signed(cpu.getRegister(instruction.rs1), 32) >> (instruction.imm%32))
                cpu.setPC(cpu.getPC() + 4)
                return False

            #Arithmetic
            case RType(opcode=0b0110011, funct3=0b000, funct7=0b0000000): #ADD
                cpu.setRegister(instruction.rd, cpu.getRegister(instruction.rs1) + cpu.getRegister(instruction.rs2))
                cpu.setPC(cpu.getPC() + 4)
                return False
            case RType(opcode=0b0110011, funct3=0b000, funct7=0b0100000): #SUB
                cpu.setRegister(instruction.rd, cpu.getRegister(instruction.rs1) - cpu.getRegister(instruction.rs2))
                cpu.setPC(cpu.getPC() + 4)
                return False
            case RType(opcode=0b0110011, funct3=0b001, funct7=0b0000000): #SLL
                cpu.setRegister(instruction.rd, cpu.getRegister(instruction.rs1) << (cpu.getRegister(instruction.rs2)%32))
                cpu.setPC(cpu.getPC() + 4)
                return False
            case RType(opcode=0b0110011, funct3=0b010, funct7=0b0000000): #SLT
                cpu.setRegister(instruction.rd, 1 if signed(cpu.getRegister(instruction.rs1),32) < signed(cpu.getRegister(instruction.rs2),32) else 0)
                cpu.setPC(cpu.getPC() + 4)
                return False
            case RType(opcode=0b0110011, funct3=0b011, funct7=0b0000000): #SLTU
                cpu.setRegister(instruction.rd, 1 if cpu.getRegister(instruction.rs1) < cpu.getRegister(instruction.rs2) else 0)
                cpu.setPC(cpu.getPC() + 4)
                return False
            case RType(opcode=0b0110011, funct3=0b100, funct7=0b0000000): #XOR
                cpu.setRegister(instruction.rd, cpu.getRegister(instruction.rs1) ^ cpu.getRegister(instruction.rs2))
                cpu.setPC(cpu.getPC() + 4)
                return False
            case RType(opcode=0b0110011, funct3=0b101, funct7=0b0000000): #SRL
                cpu.setRegister(instruction.rd, cpu.getRegister(instruction.rs1) >> (cpu.getRegister(instruction.rs2)%32))
                cpu.setPC(cpu.getPC() + 4)
                return False
            case RType(opcode=0b0110011, funct3=0b101, funct7=0b0100000): #SRA
                cpu.setRegister(instruction.rd, signed(cpu.getRegister(instruction.rs1), 32) >> (cpu.getRegister(instruction.rs2)%32))
                cpu.setPC(cpu.getPC() + 4)
                return False
            case RType(opcode=0b0110011, funct3=0b110, funct7=0b0000000): #OR
                cpu.setRegister(instruction.rd, cpu.getRegister(instruction.rs1) | cpu.getRegister(instruction.rs2))
                cpu.setPC(cpu.getPC() + 4)
                return False
            case RType(opcode=0b0110011, funct3=0b111, funct7=0b0000000): #AND
                cpu.setRegister(instruction.rd, cpu.getRegister(instruction.rs1) & cpu.getRegister(instruction.rs2))
                cpu.setPC(cpu.getPC() + 4)
                return False

            case _:
                raise ValueError(f"Unsupported instruction {instruction!r} at pc 0x{cpu.getPC():x}")

class CPU:
    def __init__(self,path):
        codeImporter = importCode(path)
        self.registers = registerFile()
        self.memory = memory(1024*1024)
        self.loadIntoMemory(codeImporter.extractCode())
        self.running = False
        self.executer = codeExecuter()
        self.pc = 0

    def loadIntoMemory(self, instructions):
        for n, word in enumerate(instructions):
            self.setMemory(4*n, word, 4)

    def setRegister(self, rd, val):
        self.registers.setRegister(rd, val%regSize)

    def getRegister(self, rd):
        return self.registers.getRegister(rd)

    def getPC(self):
        return self.pc

    def setPC(self, pc):
        self.pc = (pc%regSize)

    def executeInstruction(self,instruction):
        typeOfInstruction = self.getTypeOfInstructions(instruction)
        stopInstruction = self.executer.executeInstruction(typeOfInstruction, self)
        if stopInstruction:
            self.running = False

    def getTypeOfInstructions(self, instruction):
        opcode = instruction & 0x7f
        if opcode in typeByOpcode:
            instructionClass = typeByOpcode[opcode]
            return instructionClass(instruction)
        else:
            raise ValueError(f"Unknown opcode {opcode:b} in instruction {instruction:x}")

    def start(self):
        self.running = True
        while self.running:
            self.executeInstruction(self.getMemory(self.pc,4))

    def printRegisters(self):
        self.registers.printRegisters()

    def getMemory(self, adress, bytes):
        val = 0
        for i in reversed(range(bytes)):
            val = (val << 8) | (self.memory.getAdress((adress + i) % self.memory.getSize()))
        return val

    def setMemory(self, adress, value, bytes):
        adress = adress % self.memory.getSize() #Wrap adresses because tests set sp to 4GB, outside of 1MB
        for i in range(bytes):
            self.memory.setAdress(adress, value)
            value = value >> 8
            adress += 1