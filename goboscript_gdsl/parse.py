from typing import Literal

from .cls import *


def snake_to_pascal(s: str):
    return "".join(x.title() for x in s.split("_"))


def table_split(table: str, n: int):
    xs = table.split()
    xs.extend([""] * (n - len(xs)))
    return xs


class GDSLDecoder:
    def __init__(self, debug: bool = True):
        self.data = None
        self.debug = debug

    def load(self, data: str):
        self.data = data

    def parse(self) -> GDSLData:
        # Maybe split this into a bunch of methods to make it less messy/long
        ret = GDSLData()

        old_opcode = ""
        old_input = ""

        old_lhs = ""
        old_rhs = ""

        old_fields: list[str] = []
        old_menu = ""
        opcode_prefix = ""
        old_args = ""

        section: Literal["UNARY", "BINARY", "BLOCKS", "REPORTERS"] | None = None
        lines = iter(open("gdsl.txt"))

        for line in lines:
            line = line[:-1].strip()

            if line.startswith("#") or not line:
                continue

            if self.debug:
                print(line)

            if line in ["UNARY OPERATORS", "BINARY OPERATORS", "BLOCKS", "REPORTERS"]:
                section = line.split()[0]  # type: ignore
                next(lines, None)
                next(lines, None)
                next(lines, None)
                continue

            if section == "UNARY":
                if line.endswith("~"):
                    ret.un_ops[line.removesuffix("~")] = None
                    continue

                table, fields = line.split("|")
                fields = fields.strip()

                fields = (
                    dict(
                        (old_fields[i] if key == "..." else key, value)
                        for i, (key, value) in enumerate(
                            x.split("=") for x in fields.strip().split(",")
                        )
                    )
                    if fields
                    else {}
                )

                old_fields = list(fields.keys())
                variant, opcode, inp = table.split()

                if opcode == "...":
                    opcode = old_opcode
                else:
                    opcode = "operator_" + opcode
                    old_opcode = opcode

                if inp == "...":
                    inp = old_input
                else:
                    old_input = inp

                ret.un_ops[variant] = UnOp(opcode, inp, fields)

            elif section == "BINARY":
                if line.endswith("~"):
                    ret.bin_ops[line.removesuffix("~")] = None
                    continue

                variant, opcode, lhs, rhs = line.split()

                if opcode == "...":
                    opcode = old_opcode
                else:
                    opcode = "operator_" + opcode
                    old_opcode = opcode

                if lhs == "...":
                    lhs = old_lhs
                else:
                    old_lhs = lhs

                if rhs == "...":
                    rhs = old_rhs
                else:
                    old_rhs = rhs

                ret.bin_ops[variant] = BinOp(opcode, lhs, rhs)

            else:
                if line.startswith("["):
                    opcode_prefix = line.split("]")[0].removeprefix("[")
                    continue

                table, fields, menu = line.split("|")
                menu = menu.strip()

                if menu:
                    input_opcode, default = menu.split("=")
                    if input_opcode == "...":
                        input_opcode = old_menu

                    old_menu = input_opcode
                    inp, opcode = input_opcode.split(":")

                    if "@" in inp:
                        inp, fld = inp.split("@")
                    else:
                        fld = inp

                    menu = Menu(
                        input=inp,
                        field=fld,
                        opcode=opcode,
                        default=default,
                    )

                else:
                    menu = None

                _fields = fields.strip()

                if _fields:
                    fields = {}
                    for i, (key, value) in enumerate(
                            x.split("=") for x in _fields.strip().split(",")
                    ):
                        if key == "...":
                            key = old_fields[i]
                        fields[key] = value

                else:
                    fields = {}

                old_fields = list(fields.keys())
                name, opcode, args = table_split(table, 3)
                variant = snake_to_pascal(name)

                if opcode == "...":
                    opcode = old_opcode
                else:
                    old_opcode = opcode

                opcode = f"{opcode_prefix}_{opcode}"
                if args == "...":
                    args = old_args
                else:
                    old_args = args

                args = args.split(",") if args else []
                if section == "BLOCKS":
                    container = ret.blocks
                else:
                    container = ret.reporters

                if variant in container:
                    block = container[variant]

                    if not isinstance(block, list):
                        block = [block]

                    block.append(Block(name, opcode, args, fields, menu))
                    container[variant] = block

                else:
                    container[variant] = Block(name, opcode, args, fields, menu)

        return ret
