# mips_utils.py

TIPOS = {
    'add': 'R',
    'sub': 'R',
    'and': 'R',
    'or': 'R',
    'slt': 'R',
    'sll': 'R',  # Nueva instrucción
    'lw': 'I',
    'sw': 'I',
    'beq': 'I',
    'bne': 'I',  # Nueva instrucción
    'addi': 'I', # Nueva instrucción
    'j': 'J',
    'jal': 'J',
}

OPCODES = {
    'R': '000000',
    'lw': '100011',
    'sw': '101011',
    'beq': '000100',
    'bne': '000101',  # Nuevo opcode para bne
    'addi': '001000', # Nuevo opcode para addi
    'j': '000010',
    'jal': '000011',
}

FUNCTS = {
    'add': '100000',
    'sub': '100010',
    'and': '100100',
    'or':  '100101',
    'slt': '101010',
    'sll': '000000',  # Nuevo funct para sll
}

REGISTROS = {
    '$zero': 0, '$0': 0,  # Agregado $0 como alias de $zero
    '$at': 1,
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
    """Convierte un número a binario con un número específico de bits, manejando negativos (complemento a 2)."""
    if num < 0:
        # Calcular complemento a 2 para números negativos
        num = (1 << bits) + num
    # Formatea el número a binario, rellenando con ceros a la izquierda
    # y tomando solo los 'bits' menos significativos si el número es muy grande (para positivos)
    # o después de la conversión a complemento a 2.
    return format(num, f'0{bits}b')[-bits:]


def registro_a_bin(reg):
    if reg not in REGISTROS:
        raise ValueError(f'Registro inválido: {reg}')
    return a_binario(REGISTROS[reg], 5)

def procesar_instruccion(instr):
    try:
        partes = instr.replace(',', '').split()
        if not partes:
            return {'error': 'No se ingresó ninguna instrucción.'}

        opcode_str = partes[0].lower() # Convertir a minúsculas para consistencia
        if opcode_str not in TIPOS:
            return {'error': f'Opcode "{opcode_str}" no reconocido.'}

        tipo = TIPOS[opcode_str]

        def validar_y_obtener_registro(reg_str):
            if reg_str not in REGISTROS:
                raise ValueError(f'Registro inválido: {reg_str}')
            return reg_str

        def parse_inmediato(imm_str, bits=16):
            try:
                # Permitir números hexadecimales (ej: 0x10) y decimales
                return int(imm_str, 0) # El 0 como base auto-detecta (decimal, 0x para hex)
            except ValueError:
                raise ValueError(f'Inmediato/Offset inválido: {imm_str}')

        binario = ""
        hex_val = ""
        explicacion = ""
        campos = {}

        if tipo == 'R':
            bin_opcode_val = OPCODES['R']
            funct_val = FUNCTS.get(opcode_str)
            if funct_val is None:
                 return {'error': f'Funct no definido para la instrucción R: {opcode_str}'}

            if opcode_str == 'sll':
                if len(partes) != 4:
                    return {'error': f'Instrucción {opcode_str} requiere 3 operandos: {opcode_str} rd, rt, shamt.'}
                rd_str, rt_str, shamt_str = partes[1], partes[2], partes[3]
                
                rd = validar_y_obtener_registro(rd_str)
                rt = validar_y_obtener_registro(rt_str)
                try:
                    shamt_val = int(shamt_str)
                    if not (0 <= shamt_val < 32):
                        raise ValueError("Shamt debe estar entre 0 y 31.")
                except ValueError as e:
                    return {'error': f'Valor de shamt inválido para {opcode_str}: {shamt_str}. {e}'}

                bin_rd = registro_a_bin(rd)
                bin_rt = registro_a_bin(rt)
                bin_rs = '00000' # rs no se usa en sll, se pone a 0
                bin_shamt = a_binario(shamt_val, 5)
                
                binario = bin_opcode_val + bin_rs + bin_rt + bin_rd + bin_shamt + funct_val
                explicacion = f'{opcode_str}: Desplaza el registro {rt} a la izquierda por {shamt_val} bits y guarda el resultado en {rd}.'
                campos = {
                    'opcode': bin_opcode_val, 'rs': bin_rs, 'rt': bin_rt,
                    'rd': bin_rd, 'shamt': bin_shamt, 'funct': funct_val
                }
            else: # Otras instrucciones R (add, sub, and, or, slt)
                if len(partes) != 4:
                    return {'error': f'Instrucción tipo R "{opcode_str}" requiere 3 registros. Se recibieron {len(partes)-1}.'}
                rd_str, rs_str, rt_str = partes[1], partes[2], partes[3]
                
                rd = validar_y_obtener_registro(rd_str)
                rs = validar_y_obtener_registro(rs_str)
                rt = validar_y_obtener_registro(rt_str)

                bin_rs = registro_a_bin(rs)
                bin_rt = registro_a_bin(rt)
                bin_rd = registro_a_bin(rd)
                bin_shamt = '00000'
                
                binario = bin_opcode_val + bin_rs + bin_rt + bin_rd + bin_shamt + funct_val
                explicacion = f'{opcode_str}: Realiza la operación entre {rs} y {rt}, guarda el resultado en {rd}.'
                campos = {
                    'opcode': bin_opcode_val, 'rs': bin_rs, 'rt': bin_rt,
                    'rd': bin_rd, 'shamt': bin_shamt, 'funct': funct_val
                }

        elif tipo == 'I':
            bin_opcode_val = OPCODES[opcode_str]
            
            if opcode_str in ['lw', 'sw']:
                if len(partes) != 3:
                    return {'error': f'Instrucción {opcode_str} requiere formato: {opcode_str} rt, offset(rs).'}
                rt_str = partes[1]
                offset_reg_str = partes[2]
                
                rt = validar_y_obtener_registro(rt_str)
                if '(' not in offset_reg_str or ')' not in offset_reg_str:
                    return {'error': f'Formato offset incorrecto en {offset_reg_str}. Debe ser offset(registro).'}
                
                try:
                    offset_str, reg_base_str_with_paren = offset_reg_str.split('(')
                    reg_base_str = reg_base_str_with_paren.replace(')', '')
                except ValueError:
                     return {'error': f'Formato offset(registro) incorrecto: {offset_reg_str}'}

                rs = validar_y_obtener_registro(reg_base_str)
                inmediato_val = parse_inmediato(offset_str)

                bin_rs = registro_a_bin(rs)
                bin_rt = registro_a_bin(rt)
                bin_imm = a_binario(inmediato_val, 16)
                
                binario = bin_opcode_val + bin_rs + bin_rt + bin_imm
                explicacion = f'{opcode_str}: Carga/Almacena palabra entre registro {rt} y dirección de memoria {inmediato_val}({rs}).'
                campos = {'opcode': bin_opcode_val, 'rs': bin_rs, 'rt': bin_rt, 'inmediato': bin_imm}

            elif opcode_str in ['beq', 'bne']:
                if len(partes) != 4:
                    return {'error': f'Instrucción {opcode_str} requiere 3 argumentos: {opcode_str} rs, rt, offset.'}
                rs_str, rt_str, imm_str = partes[1], partes[2], partes[3]
                
                rs = validar_y_obtener_registro(rs_str)
                rt = validar_y_obtener_registro(rt_str)
                inmediato_val = parse_inmediato(imm_str) # El offset es relativo a PC+4, pero aquí solo codificamos el valor

                bin_rs = registro_a_bin(rs)
                bin_rt = registro_a_bin(rt)
                bin_imm = a_binario(inmediato_val, 16)
                
                binario = bin_opcode_val + bin_rs + bin_rt + bin_imm
                accion = "salta" if opcode_str == "beq" else "salta si no son iguales"
                condicion = "si son iguales" if opcode_str == "beq" else "si no son iguales"
                explicacion = f'{opcode_str}: Compara {rs} y {rt}. Si {condicion}, salta a la etiqueta/offset {inmediato_val}.'
                campos = {'opcode': bin_opcode_val, 'rs': bin_rs, 'rt': bin_rt, 'inmediato': bin_imm}
            
            elif opcode_str == 'addi':
                if len(partes) != 4:
                    return {'error': f'Instrucción {opcode_str} requiere 3 argumentos: {opcode_str} rt, rs, inmediato.'}
                rt_str, rs_str, imm_str = partes[1], partes[2], partes[3]
                
                rt = validar_y_obtener_registro(rt_str)
                rs = validar_y_obtener_registro(rs_str)
                inmediato_val = parse_inmediato(imm_str)

                bin_rs = registro_a_bin(rs)
                bin_rt = registro_a_bin(rt)
                bin_imm = a_binario(inmediato_val, 16)
                
                binario = bin_opcode_val + bin_rs + bin_rt + bin_imm
                explicacion = f'{opcode_str}: Suma el contenido de {rs} con el inmediato {inmediato_val} y guarda en {rt}.'
                campos = {'opcode': bin_opcode_val, 'rs': bin_rs, 'rt': bin_rt, 'inmediato': bin_imm}
            else:
                return {'error': f'Instrucción tipo I "{opcode_str}" no soportada o con formato incorrecto.'}

        elif tipo == 'J':
            if len(partes) != 2:
                return {'error': f'Instrucción {opcode_str} requiere un solo argumento (dirección/etiqueta).'}
            
            addr_str = partes[1]
            try:
                # Permitir direcciones decimales o hexadecimales (ej: 0x00400020)
                # La dirección en la instrucción J es de 26 bits.
                # Típicamente, la dirección de salto es una dirección de byte,
                # y el campo de dirección en la instrucción es (dirección_byte / 4).
                # Sin embargo, si el valor de la imagen (ej: 1024, 0x00400020) ya es
                # el valor que va en el campo de 26 bits, no se divide.
                # Asumiremos que es el valor directo para el campo de 26 bits por ahora.
                address_val = int(addr_str, 0) # base 0 auto-detecta
            except ValueError:
                return {'error': f'Dirección inválida para {opcode_str}: {addr_str}'}

            bin_opcode_val = OPCODES[opcode_str]
            # Asegurarse de que la dirección cabe en 26 bits.
            # Si la dirección es más grande, se truncará por a_binario, lo cual podría ser o no el comportamiento deseado.
            # Para un salto real, la dirección completa se forma con parte del PC. Aquí solo codificamos el campo.
            if address_val < 0 or address_val >= (1 << 26) : # Para direcciones de salto directas en el campo, no suelen ser negativas.
                 # Si la dirección dada es una dirección de byte completa como 0x00400020,
                 # el campo de 26 bits debería ser (address_val // 4) & ((1 << 26) - 1)
                 # Si 1024 o 0x00400020 ya es el 'instr_index'
                 # address_for_field = address_val
                 # Si es una dirección de byte y debe ser convertida:
                 # address_for_field = address_val // 4 # Descartar los 2 bits LSB (ya que las instrucciones están alineadas a palabras)
                 # Ejemplo: si 0x00400020 es la dirección de byte, el campo es 0x00100008
                 # El enunciado "j 1024" o "j 0x00400020" usualmente implica que este es el target.
                 # Si el número ya es el "address index" (target_address / 4) entonces se usa directo.
                 # Vamos a asumir que el número proporcionado es el valor para el campo de 26 bits.
                 # Si fuera una dirección de byte completa, se debería dividir por 4.
                 # Por simplicidad y para que coincida con la imagen, tomaremos el valor tal cual.
                 pass # No se hace nada especial aquí, a_binario lo manejará.

            bin_addr = a_binario(address_val, 26)
            binario = bin_opcode_val + bin_addr
            explicacion = f'{opcode_str}: Salto incondicional a la dirección (campo de 26 bits) {address_val} (0x{address_val:x}).'
            campos = {'opcode': bin_opcode_val, 'direccion': bin_addr}
        else:
            return {'error': 'Tipo de instrucción no reconocido internamente.'}

        hex_val = f'0x{int(binario, 2):08x}' # Formatear a 8 dígitos hexadecimales (32 bits)

        return {
            'instruccion': instr,
            'tipo': tipo,
            'binario': binario,
            'hexadecimal': hex_val,
            'campos': campos,
            'explicacion': explicacion
        }
    except ValueError as ve:
        return {'error': str(ve)}
    except Exception as e:
        # Para depuración, puedes imprimir la traza completa del error
        # import traceback
        # traceback.print_exc()
        return {'error': f'Error procesando instrucción "{instr}": {str(e)}'}

# --- Ejemplo de uso (puedes comentar o borrar esto) ---
if __name__ == '__main__':
    instrucciones_ejemplo = [
        "add $t0, $t1, $t2",
        "sub $s1, $s2, $s3",
        "and $a0, $a1, $a2",
        "addi $t0, $t1, 10",
        "addi $s1, $s1, -5",
        "lw $s0, 4($t0)",
        "sw $s0, 8($sp)", # Ejemplo de sw
        "beq $t0, $t1, 3", # El '3' es un offset de instrucciones
        "bne $t0, $t1, -2", # El '-2' es un offset de instrucciones
        "j 1024",
        "j 0x00400020", # Esto será truncado a 26 bits si es muy grande, o interpretado como el valor para el campo
        "jal 2048",
        "sll $t0, $t1, 3",
        "slt $s0, $t0, $t1",
        "or $t3, $t4, $t5", # Ejemplo de or
        "addi $zero, $zero, 0" # nop (a veces)
    ]

    for instr in instrucciones_ejemplo:
        resultado = procesar_instruccion(instr)
        print(f"Instrucción: {instr}")
        if 'error' in resultado:
            print(f"  Error: {resultado['error']}")
        else:
            print(f"  Tipo: {resultado['tipo']}")
            print(f"  Binario: {resultado['binario']}")
            print(f"  Hex: {resultado['hexadecimal']}")
            print(f"  Campos: {resultado['campos']}")
            print(f"  Explicación: {resultado['explicacion']}")
        print("-" * 30)

    # Prueba específica para 'j 0x00400020'
    # En MIPS, el campo de dirección de 26 bits para 'j' es la dirección de palabra.
    # Si 0x00400020 es la dirección de byte, el campo de 26 bits sería 0x00400020 / 4 = 0x00100008.
    # El código actual toma 0x00400020 directamente y lo mete en 26 bits.
    # Si la intención es que 0x00400020 sea la dirección de byte:
    # address_byte = 0x00400020
    # address_field_val = address_byte // 4
    # print(f"\nPrueba 'j 0x00400020' (interpretando como dirección de byte):")
    # print(f"  Valor para el campo de 26 bits sería: {hex(address_field_val)} ({address_field_val})")
    # print(f"  Binario del campo: {a_binario(address_field_val, 26)}")
    #
    # Para `j 1024`:
    # Si 1024 es la dirección de byte:
    # address_byte_1024 = 1024
    # address_field_1024 = address_byte_1024 // 4 # = 256
    # print(f"\nPrueba 'j 1024' (interpretando como dirección de byte):")
    # print(f"  Valor para el campo de 26 bits sería: {hex(address_field_1024)} ({address_field_1024})")
    # print(f"  Binario del campo: {a_binario(address_field_1024, 26)}")
    # El código actual, con 'j 1024', usa 1024 directamente como valor para el campo de 26 bits.
    # Esto es común si '1024' es una etiqueta que ya resuelve al índice de instrucción (word address).