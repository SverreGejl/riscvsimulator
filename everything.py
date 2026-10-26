class importCode:
    def __init__(self,path):
        self.path = path

    def extractCode(self):
        instructions = []
        #FIX THIS SHIT
        with open(self.path,'r') as f:
            code = f.read()
            instructions.append(instruction(code))
        return instructions

class memory:
    def __init__(self,size):
        self.memory = [0 for i in range(size)]

    def getAdress(self,address):
        return self.memory[address]

    def setAdress(self,address, val):
        self.memory[address] = val

class instruction:
    def __init__(self,code):
        #FIX THIS SHIT
        self.opcode = code[1:2]
        self.regA = code[2:4]
        self.regB = code[4:6]
        self.valA = code[8:10]
        self.valB = code[10:12]

class registerFile:
    def __init__(self):
        self.registers = [0 for i in range(32)]

    def setRegister(self,idx,val):
        self.registers[idx] = val

    def getRegister(self,idx):
        return self.registers[idx]

class CPU:
    def __init__(self,path):
        codeImporter = importCode(path)
        self.registers = registerFile()
        self.memory = memory(1024*1024)
        self.instructions = codeImporter.extractCode()
        self.pc = 0

    def executeInstruction(self,task : instruction):
        self.pc += 4

    def start(self):
        while self.pc < 4*(len(self.instructions)-1):
            self.executeInstruction(self.pc)

    def printRegisters(self):
        pass

cpu = CPU("./testcode.asm")
cpu.start()
cpu.printRegisters()