from CPU.instructions import instr_dict
from CPU.ram import RAM
from CPU.registers import Registers


class CPU:
    def __init__(self, ram):
        # La memoria RAM debera ser cargada desde la ubicacion donde se cree la instancia
        self.ram = ram
        self.reg = Registers()
        self.running = True

    def step(self):

        print(self.ram.read(self.reg.PC))
        # FETCH
        opcode = int(self.ram.read(self.reg.PC), 2)

        # DECODE
        func, size = instr_dict[opcode]

        # FETCH COMPLETO
        instr = self.ram.read_block(self.reg.PC, size)
        self.reg.IR = instr

        # EXECUTE
        # En caso de que jumped sea verdadero entonces la funcion habra actualizado el PC
        jumped = func(self, self.reg, self.ram)

        # UPDATE PC
        if not jumped:
            self.reg.increment_PC(size)
