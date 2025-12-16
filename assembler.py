#!/usr/bin/env python3
import argparse
import sys
from dataclasses import dataclass
from typing import List, Optional

# ==== ОПКОМАНДЫ УВМ ====
OPCODES = {
    "LOAD_CONST": 42,
    "LOAD_MEM": 23,
    "STORE_MEM": 1,
    "BITREVERSE": 60,
}

# ==== ОПИСАНИЕ ИНСТРУКЦИИ ====
@dataclass
class Instruction:
    mnemonic: str
    A: int
    B: Optional[int] = None

    def to_ir(self):
        return {
            "opcode": self.A,
            "A": self.A,
            "B": self.B
        }

# ==== ПАРСЕР ====
def parse_line(line: str, line_no: int) -> Optional[Instruction]:
    # Удаляем комментарии
    line = line.split(";")[0].strip()
    if not line:
        return None

    parts = line.split()
    mnemonic = parts[0].upper()

    if mnemonic not in OPCODES:
        raise SyntaxError(f"Строка {line_no}: неизвестная команда {mnemonic}")

    opcode = OPCODES[mnemonic]

    if mnemonic in ("LOAD_CONST", "LOAD_MEM"):
        if len(parts) != 2:
            raise SyntaxError(f"Строка {line_no}: ожидается один аргумент")
        try:
            operand = int(parts[1])
        except ValueError:
            raise SyntaxError(f"Строка {line_no}: аргумент должен быть числом")
        return Instruction(mnemonic, opcode, operand)

    if mnemonic in ("STORE_MEM", "BITREVERSE"):
        if len(parts) != 1:
            raise SyntaxError(f"Строка {line_no}: команда без аргументов")
        return Instruction(mnemonic, opcode)

    return None

# ==== АССЕМБЛИРОВАНИЕ В IR ====
def assemble_to_ir(source_lines: List[str]) -> List[Instruction]:
    instructions = []
    for i, line in enumerate(source_lines, start=1):
        instr = parse_line(line, i)
        if instr:
            instructions.append(instr)
    return instructions

# ==== ВЫВОД IR В ТЕСТОВОМ РЕЖИМЕ ====
def print_ir(ir: List[Instruction]):
    for idx, instr in enumerate(ir):
        print(f"Instruction {idx}:")
        print(f"  A = {instr.A}")
        if instr.B is not None:
            print(f"  B = {instr.B}")

# ==== КОДИРОВАНИЕ В МАШИННЫЙ КОД ====
def encode_instruction(instr: Instruction) -> bytes:
    """Преобразует Instruction в 4-байтовую команду."""
    A = instr.A
    B = instr.B or 0

    if instr.mnemonic == "LOAD_CONST":
        # B: биты 6-21, A: 0-5
        word = (B << 6) | A
    elif instr.mnemonic == "LOAD_MEM":
        # B: биты 6-29, A: 0-5
        word = (B << 6) | A
    else:
        # STORE_MEM и BITREVERSE — без операнда
        word = A

    return word.to_bytes(4, byteorder='little')

def write_binary_file(ir: List[Instruction], output_path: str):
    with open(output_path, "wb") as f:
        for instr in ir:
            f.write(encode_instruction(instr))

def print_machine_code(ir: List[Instruction]):
    print(f"Number of instructions: {len(ir)}")
    for idx, instr in enumerate(ir):
        bytes_seq = encode_instruction(instr)
        print(f"Instr {idx}: {' '.join(f'0x{b:02X}' for b in bytes_seq)}")

# ==== CLI ====
def main():
    parser = argparse.ArgumentParser(description="Assembler for UVM (stages 1-2)")
    parser.add_argument("input", help="Path to input .asm file")
    parser.add_argument("output", help="Path to output binary file")
    parser.add_argument("--test", action="store_true", help="Test mode (show IR and machine code)")

    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            lines = f.readlines()

        ir = assemble_to_ir(lines)

        if args.test:
            print("=== Intermediate Representation (IR) ===")
            print_ir(ir)
            print("\n=== Machine code ===")
            print_machine_code(ir)

        write_binary_file(ir, args.output)
        print(f"Binary file written: {args.output} ({len(ir)} instructions)")

    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
