from dataclasses import dataclass, field


@dataclass
class UnOp:
    opcode: str
    input: str
    fields: dict[str, str]


@dataclass
class BinOp:
    opcode: str
    lhs: str
    rhs: str


@dataclass
class Menu:
    input: str
    field: str
    opcode: str
    default: str


@dataclass
class Block:
    name: str
    opcode: str
    args: list[str]
    fields: dict[str, str]
    menu: Menu | None


@dataclass
class GDSLData:
    un_ops: dict[str, UnOp | None] = field(default_factory=lambda: {})
    bin_ops: dict[str, BinOp | None] = field(default_factory=lambda: {})
    blocks: dict[str, Block | list[Block]] = field(default_factory=lambda: {})
    reporters: dict[str, Block | list[Block]] = field(default_factory=lambda: {})
