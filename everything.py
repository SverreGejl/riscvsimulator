from instructionType import typeByOpcode, IType

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
        self.memory = [0 for i in range(size)]

    def getAdress(self,address):
        return self.memory[address]

    def setAdress(self,address, val):
        self.memory[address] = val

class registerFile:
    def __init__(self):
        self.registers = [0 for i in range(32)]

    def setRegister(self,idx,val):
        self.registers[idx] = val

    def getRegister(self,idx):
        return self.registers[idx]

    def printRegisters(self):
        for i in range(32):
            print(i, self.registers[i])


class codeExecuter:
    #TODO: Mark needs to make a huge switch statement here :))))
    def executeInstruction(self, instruction: typeByOpcode):
        match instruction:
            case IType(opcode=0x73, rd=0, funct3=0, rs1=0, imm=0): #ECALL
                return True
            case _ :
                return False


class CPU:
    def __init__(self,path):
        codeImporter = importCode(path)
        self.registers = registerFile()
        self.memory = memory(1024*1024)
        self.instructions = codeImporter.extractCode()
        self.running = False
        self.executer = codeExecuter()
        self.pc = 0

    def executeInstruction(self,instruction):
        typeOfInstruction = self.getTypeOfInstructions(instruction)
        stopInstruction = self.executer.executeInstruction(typeOfInstruction)
        if not stopInstruction:
            self.pc += 4
        else:
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
            instructionIndex = int(self.pc/4)
            self.executeInstruction(self.instructions[instructionIndex])

    def printRegisters(self):
        self.registers.printRegisters()