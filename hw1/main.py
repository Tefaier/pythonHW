from typing import Tuple

class Tensor:
    def __init__(self, dimensions: int | Tuple[int, ...], data: list[int]):
        self.dimensions = dimensions
        self.data = data

    def __repr__(self) -> str:
        return self.data.__repr__()

class Matrix(Tensor):
    def __init__(self, dimensions: Tuple[int, int], data: list[int]):
        super().__init__(dimensions, data)
        self.two_dim_data = []
        for row_index in range(0, dimensions[0]):
            self.two_dim_data.append(data[row_index * dimensions[1] : (row_index + 1) * dimensions[1]])

    def conv_rc2i(self, r_c: Tuple[int, int]) -> int:
        return r_c[0] * self.dimensions[0] + r_c[1]

    def conv_i2rc(self, index: int) -> Tuple[int, int]:
        return index // self.dimensions[1], index - self.dimensions[1] * (index // self.dimensions[1])

    def __str__(self) -> str:
        result = "["
        longest_sizes = [0] * len(self.two_dim_data[0])
        for row in self.two_dim_data:
            for index, value in enumerate(row):
                longest_sizes[index] = max(longest_sizes[index], len(str(value)))
        for row in self.two_dim_data:
            result += '\n '
            for index, value in enumerate(row):
                result += ' ' * (2 + longest_sizes[index] - len(str(value)))
                result += str(value)
            result += '\n'
        return result + "]"

    def __getitem__(self, item):
        if type(item) is list:
            return Matrix((len(item), self.dimensions[1]), [value for index in item for value in self.two_dim_data[index]])
        if type(item) is int:
            return Matrix((1, self.dimensions[1]), self.two_dim_data[item])
        if type(item) is slice:
            filtered: list[list[int]] | list[int] = self.two_dim_data[item]
            if type(filtered[0]) is int:
                return Matrix((1, self.dimensions[1]), filtered)
            else:
                return Matrix((len(filtered), self.dimensions[1]), [value for row in filtered for value in row])
        if type(item) is tuple:
            rule_1 = item[0]
            rule_2 = item[1]
            if type(rule_1) is int and type(rule_2) is int:
                return self.two_dim_data[rule_1][rule_2]
            if type(rule_1) is list:
                rows = [self.two_dim_data[index] for index in rule_1]
            else:
                rows = self.two_dim_data[rule_1]
            if type(rows[0]) is int:
                rows = [rows]
            if type(rule_2) is list:
                rows = [[row[index] for index in rule_2] for row in rows]
            else:
                rows = [[row[rule_2]] if type(row[rule_2]) is int else row[rule_2] for row in rows]
            if type(rows[0]) is int:
                rows = [rows]
            return Matrix((len(rows), len(rows[0])), [value for row in rows for value in row])
