class Expression:
    def __init__(self):
        self.char = None
        self.expr = None
        self.expr1 = None
        self.expr2 = None

    def __str__(self) -> str:
        pass


class SymbolExpression(Expression):
    char: str

    def __init__(self, c: str):
        super().__init__()
        self.char = c

    def __str__(self):
        return self.char

    def __repr__(self):
        return "Symbol(" + self.char + ")"


class StarExpression(Expression):
    expr: Expression

    def __init__(self, expr: Expression):
        super().__init__()
        self.expr = expr

    def __str__(self):
        string = "(" + repr(self.expr) + ")*"
        return string

    def __repr__(self):
        string = "Star(" + repr(self.expr) + ")"
        return string


class PlusExpression(Expression):
    expr: Expression

    def __init__(self, expr: Expression):
        super().__init__()
        self.expr = expr

    def __str__(self):
        string = "(" + str(self.expr) + ")+"
        return string

    def __repr__(self):
        string = "Plus(" + repr(self.expr) + ")"
        return string


class ConcatenationExpression(Expression):
    expr1: Expression
    expr2: Expression

    def __init__(self, expr1: Expression, expr2: Expression):
        super().__init__()
        self.expr1 = expr1
        self.expr2 = expr2

    def __str__(self):
        string = str(self.expr1) + str(self.expr2)
        return string

    def __repr__(self):
        string = "Concat(" + repr(self.expr1) + ", " + repr(self.expr2) + ")"
        return string


class UnionExpression(Expression):
    expr1: Expression
    expr2: Expression

    def __init__(self, expr1: Expression, expr2: Expression):
        super().__init__()
        self.expr1 = expr1
        self.expr2 = expr2

    def __str__(self):
        string = "(" + str(self.expr1) + " U " + str(self.expr2) + ")"
        return string

    def __repr__(self):
        string = "Union(" + repr(self.expr1) + ", " + repr(self.expr2) + ")"
        return string


def create_expr(s: str) -> Expression:
    stack = []
    expression_strings = list(s.split())
    expression_strings.reverse()
    for x in expression_strings:
        if x == "STAR":
            e = stack[-1]
            stack.pop()
            stack.append(StarExpression(e))
        elif x == "UNION":
            e1 = stack[-1]
            stack.pop()
            e2 = stack[-1]
            stack.pop()
            stack.append(UnionExpression(e1, e2))
        elif x == "CONCAT":
            e1 = stack[-1]
            stack.pop()
            e2 = stack[-1]
            stack.pop()
            stack.append(ConcatenationExpression(e1, e2))
        elif x == "PLUS":
            e = stack[-1]
            stack.pop()
            stack.append(PlusExpression(e))
        else:
            stack.append(SymbolExpression(x))
    return stack[-1]
