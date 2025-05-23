# mips_utils.py

# Diccionario con formatos básicos (simplificado)
TIPOS = {
    'add': 'R',
    'sub': 'R',
    'and': 'R',
    'or': 'R',
    'slt': 'R',
    'lw': 'I',
    'sw': 'I',
    'beq': 'I',
    'j': 'J',
    'jal': 'J',
}

OPCODES = {
    'R': '000000',
    'lw': '100011',
    'sw': '101011',
    'beq': '000100',
    'j': '000010',
    'jal': '000011',
}

FUNCTS = {
    'add': '100000',
    'sub': '100010',
    'and': '100100',
    'or':  '100101',
    'slt': '101010',
}

REGISTROS = {
    '$zero': 0, '$at': 1,
    '$v0': 2, '$v1': 3,
    '$a0': 4, '$a1': 5, '$a2': 6, '$a3': 7,
    '$t0': 8, '$t1': 9, '$t2': 10, '$t3': 11,
    '$t4': 12, '$t5': 13, '$t6': 14, '$t7': 15,
    '$s0': 16, '$s1': 17, '$s2': 18, '$s3': 19,
    '$s4': 20, '$s5': 21, '$s6': 22, '$s7': 23,
    '$t8': 24, '$t9': 25,
    '$k0': 26, '$k1': 27,
    '$gp': 28, '$sp': 29, '$fp': 30, '$ra': 31,
}

def a_binario(num, bits):
    return format(num, f'0{bits}b')

def registro_a_bin(reg):
    return a_binario(REGISTROS.get(reg, 0), 5)

def procesar_instruccion(instr):
    try:
        partes = instr.replace(',', '').split()
        opcode = partes[0]
        tipo = TIPOS.get(opcode)
        
        if tipo == 'R':
            rd, rs, rt = partes[1], partes[2], partes[3]
            bin_opcode = OPCODES['R']
            bin_rs = registro_a_bin(rs)
            bin_rt = registro_a_bin(rt)
            bin_rd = registro_a_bin(rd)
            shamt = '00000'
            funct = FUNCTS[opcode]
            binario = bin_opcode + bin_rs + bin_rt + bin_rd + shamt + funct
            hex_val = hex(int(binario, 2))
            explicacion = f'Realiza {opcode} entre registros {rs} y {rt}, guarda resultado en {rd}.'

            campos = {
                'opcode': bin_opcode,
                'rs': bin_rs,
                'rt': bin_rt,
                'rd': bin_rd,
                'shamt': shamt,
                'funct': funct
            }
            
        elif tipo == 'I':
            if opcode in ['lw', 'sw']:
                rt = partes[1]
                offset_reg = partes[2]  # ej. 4($t1)
                offset, reg = offset_reg.split('(')
                reg = reg.replace(')', '')
                bin_opcode = OPCODES[opcode]
                bin_rs = registro_a_bin(reg)
                bin_rt = registro_a_bin(rt)
                bin_imm = a_binario(int(offset), 16)
                binario = bin_opcode + bin_rs + bin_rt + bin_imm
                hex_val = hex(int(binario, 2))
                explicacion = f'{opcode} carga/almacena desde {offset}({reg}) en {rt}.'

                campos = {
                    'opcode': bin_opcode,
                    'rs': bin_rs,
                    'rt': bin_rt,
                    'inmediato': bin_imm
                }

            elif opcode == 'beq':
                rs, rt, imm = partes[1], partes[2], partes[3]
                bin_opcode = OPCODES[opcode]
                bin_rs = registro_a_bin(rs)
                bin_rt = registro_a_bin(rt)
                bin_imm = a_binario(int(imm), 16)
                binario = bin_opcode + bin_rs + bin_rt + bin_imm
                hex_val = hex(int(binario, 2))
                explicacion = f'Compara {rs} y {rt}, salta a offset {imm} si son iguales.'

                campos = {
                    'opcode': bin_opcode,
                    'rs': bin_rs,
                    'rt': bin_rt,
                    'inmediato': bin_imm
                }
            else:
                return {'error': 'Instrucción I no soportada aún.'}

        elif tipo == 'J':
            address = int(partes[1])
            bin_opcode = OPCODES[opcode]
            bin_addr = a_binario(address, 26)
            binario = bin_opcode + bin_addr
            hex_val = hex(int(binario, 2))
            explicacion = f'Salto incondicional a dirección {address}.'

            campos = {
                'opcode': bin_opcode,
                'direccion': bin_addr
            }
        else:
            return {'error': 'Instrucción no reconocida.'}

        return {
            'instruccion': instr,
            'tipo': tipo,
            'binario': binario,
            'hexadecimal': hex_val,
            'campos': campos,
            'explicacion': explicacion
        }
    except Exception as e:
        return {'error': f'Error procesando instrucción: {str(e)}'}
