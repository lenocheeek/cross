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

# ==== CLI ====
def main():
    parser = argparse.ArgumentParser(description="Assembler for UVM (stage 1)")
    parser.add_argument("input", help="Путь к входному .asm файлу")
    parser.add_argument("output", help="Путь к выходному бинарному файлу (пока не используется)")
    parser.add_argument("--test", action="store_true", help="Режим тестирования")

    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            lines = f.readlines()

        ir = assemble_to_ir(lines)

        if args.test:
            print_ir(ir)
        else:
            # На этапе 1 бинарный файл не генерируем
            pass

    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
