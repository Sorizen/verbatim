from dataclasses import dataclass

from app.enums import DiffOp

MATCH_COST = 0
EDIT_COST = 1


@dataclass(frozen=True)
class AlignedPair:
    op: DiffOp | None
    expected_index: int | None
    heard_index: int | None


def build_cost_table(expected: list[str], heard: list[str]) -> list[list[int]]:
    rows, columns = len(expected) + 1, len(heard) + 1
    table = [[0] * columns for _ in range(rows)]
    for row in range(rows):
        table[row][0] = row
    for column in range(columns):
        table[0][column] = column
    for row in range(1, rows):
        for column in range(1, columns):
            substitution = MATCH_COST if expected[row - 1] == heard[column - 1] else EDIT_COST
            table[row][column] = min(
                table[row - 1][column - 1] + substitution,
                table[row - 1][column] + EDIT_COST,
                table[row][column - 1] + EDIT_COST,
            )
    return table


def backtrace(table: list[list[int]], expected: list[str], heard: list[str]) -> list[AlignedPair]:
    pairs: list[AlignedPair] = []
    row, column = len(expected), len(heard)
    while row or column:
        if row and column:
            same = expected[row - 1] == heard[column - 1]
            substitution = MATCH_COST if same else EDIT_COST
            if table[row][column] == table[row - 1][column - 1] + substitution:
                pairs.append(AlignedPair(None if same else DiffOp.SUBSTITUTE, row - 1, column - 1))
                row, column = row - 1, column - 1
                continue
        if row and table[row][column] == table[row - 1][column] + EDIT_COST:
            pairs.append(AlignedPair(DiffOp.DELETE, row - 1, None))
            row -= 1
            continue
        pairs.append(AlignedPair(DiffOp.INSERT, None, column - 1))
        column -= 1
    return list(reversed(pairs))


def align_words(expected: list[str], heard: list[str]) -> list[AlignedPair]:
    return backtrace(build_cost_table(expected, heard), expected, heard)


def count_errors(pairs: list[AlignedPair]) -> int:
    return sum(1 for pair in pairs if pair.op)
