"""
ARQUITECTURA CON BUSES EXPLÍCITOS
==================================

Antes (Implícito):
─────────────────
    CPU.step()
        ↓
    self.ram.read_block(self.reg.PC, 8)  ← Acceso directo
        ↓
    Registro IR

Ahora (Explícito):
─────────────────
    CPU.step()
        ↓
    1️⃣ Pone PC en AddressBus → buses.address_bus.set_address(self.reg.PC)
        ↓
    2️⃣ Activa READ en ControlBus → buses.control_bus.set_read(True)
        ↓
    3️⃣ Lee de memoria → self.ram.read_block(address, 8)
        ↓
    4️⃣ Coloca dato en DataBus → buses.data_bus.write_data(int(instr, 2))
        ↓
    5️⃣ Desactiva READ → buses.control_bus.set_read(False)
        ↓
    Registro IR


COMPONENTES DE LOS BUSES:
========================

┌─────────────────────────────────────────────────────────────────┐
│                         ARQUITECTURA                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                       CPU                                │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │     Registers (PC, SP, R0-R15, IR, FLAGS)       │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  │                      │                                   │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │  BusInterface (coordina lectura/escritura)       │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│    │                    │                      │                │
│    └────────────────────┼──────────────────────┴────────────────┤
│                         │                                       │
│  ┌──────────────────────┴──────────────────────────────────┐   │
│  │             SISTEMAS DE BUSES EXPLÍCITOS               │   │
│  ├───────────────────────────────────────────────────────┤   │
│  │  🚌 AddressBus (32 bits): Transporta direcciones      │   │
│  │  🚌 DataBus (64 bits):    Transporta datos            │   │
│  │  🚌 ControlBus (señales):  READ, WRITE, ENABLE, etc.  │   │
│  └───────────────────────────────────────────────────────┘   │
│    │                    │                      │                │
│    └────────────────────┼──────────────────────┴────────────────┤
│                         │                                       │
│  ┌──────────────────────┴──────────────────────────────────┐   │
│  │                  MEMORIA (RAM)                          │   │
│  │  (Accesible SOLO a través de los buses)                │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘


FLUJO DE UNA LECTURA (READ CYCLE):
==================================

1. CPU coloca dirección en AddressBus:
   buses.address_bus.set_address(0x120)

2. CPU activa READ en ControlBus:
   buses.control_bus.set_read(True)
   buses.control_bus.set_enable(True)

3. Memoria entrega dato a través de DataBus:
   buses.data_bus.write_data(data)

4. CPU lee del DataBus:
   dato = buses.data_bus.read_data()

5. CPU desactiva READ:
   buses.control_bus.set_read(False)
   
   
FLUJO DE UNA ESCRITURA (WRITE CYCLE):
====================================

1. CPU coloca dirección en AddressBus:
   buses.address_bus.set_address(0x120)

2. CPU coloca dato en DataBus:
   buses.data_bus.write_data(data)

3. CPU activa WRITE en ControlBus:
   buses.control_bus.set_write(True)
   buses.control_bus.set_enable(True)

4. Memoria accede y escribe el dato

5. CPU desactiva WRITE:
   buses.control_bus.set_write(False)


ESTADO DE LOS BUSES EN CADA CICLO:
==================================

Cuando ejecutas display_state(), verás:

  BUSES (Address | Data | Control):
    Address Bus: 0x00000000
    Data Bus:    0x0000000000000000
    Control Bus: [READ=0 | WRITE=0 | ENABLE=0 | READY=1 | INTERRUPT=0 | CLOCK=0]


SEÑALES DE CONTROL:
===================

- READ (1 bit):      Solicita lectura de memoria (1=lectura, 0=no)
- WRITE (1 bit):     Solicita escritura en memoria (1=escritura, 0=no)
- ENABLE (1 bit):    Habilita la memoria (1=habilitada, 0=deshabilitada)
- READY (1 bit):     Indica si la memoria está lista (1=lista, 0=ocupada)
- INTERRUPT (1 bit): Señal de interrupción (1=interrupción, 0=ninguna)
- CLOCK (1 bit):     Pulso de reloj para sincronización


VENTAJAS DE ESTA ARQUITECTURA EXPLÍCITA:
========================================

✓ Realista: Emula cómo funciona una computadora real
✓ Visible: Puedes ver exactamente qué dato está en cada bus
✓ Debuggeable: Es fácil ver dónde ocurren los problemas
✓ Educativo: Entiendes mejor la arquitectura Von Neumann
✓ Extensible: Fácil de añadir componentes (caché, MMU, etc.)


EJEMPLO DE USO DIRECTO:
======================

# Leer de memoria:
data = cpu.read_memory_via_bus(0x0, 8)

# Escribir a memoria:
cpu.write_memory_via_bus(0x0, "11010011")

# Ver estado de buses:
cpu.display_state()  # Muestra buses + registros + memoria
"""
