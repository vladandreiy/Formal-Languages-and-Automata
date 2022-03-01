from Lexer import *
from expression import *
from main import regex_to_nfa, nfa_to_dfa


# Reduces the top of the stack that parses the Regular Expression
def reduce(stack: list, end: bool):
    # If the top of the stack has a right bracket, the expression inside it
    # can also be reduced immediately, 
    top = stack[-1]
    # If the top of the stack has either a Star or a Plus, 
    # it can be reduced immediately as it has the highest precedence
    if top == "*":
        stack.pop()
        elem = stack[-1]
        stack.pop()
        stack.append(StarExpression(elem))
    elif top == "+":
        stack.pop()
        elem = stack[-1]
        stack.pop()
        stack.append(PlusExpression(elem))

    # If the top of the stack has a right bracket, the regular expression
    # inside the brackets can be reduced, first by Concatenating all 
    # the expressions inside and then by doing the Unions, if there are any
    elif top == ")":
        left_parenthesis_index = stack[::-1].index("(")
        parenthesis = stack[len(stack) - left_parenthesis_index:len(stack) - 1]
        stack = stack[:-left_parenthesis_index - 1]
        parenthesis = reduce_concat_union(parenthesis)
        stack.append(parenthesis[0])

    # If the entire expression has been placed on the stack, the only
    # remaining operations to be done are Concatenation and Union
    elif end:
        stack = reduce_concat_union(stack)
    return stack


def reduce_concat_union(stack: list):
    # Concatenate all expressions in stack as it has higher precedence
    for i in range(len(stack) - 1, 0, -1):
        if issubclass(type(stack[i]), Expression) and issubclass(type(stack[i - 1]), Expression):
            new_elem = ConcatenationExpression(stack[i - 1], stack[i])
            stack = stack[:-2]
            stack.append(new_elem)

    # Union between expressions, if there is any union symbol
    for i in range(len(stack) - 2, 0, -1):
        if stack[i] == "|":
            new_elem = UnionExpression(stack[i - 1], stack[i + 1])
            stack = stack[:-3]
            stack.append(new_elem)
    return stack


# Reads lexer data from file, transforming Regular Expressions to DFAs
def read_lexer_regex(lexer_file: str):
    tokens = []
    regexes = []
    # Split tokens and Regular expressions
    with open(lexer_file) as input_file:
        lines = input_file.readlines()
        for line in lines:
            tokens.append(line[0:line.find(' ')])
            regexes.append(line[line.find(' ') + 1:line.rfind(';')])
            line.rstrip()

    # Create DFAs from Regular Expressions
    dfas = []
    for j in range(0, len(regexes)):
        regex = regexes[j]
        stack = []
        skip = False
        for i in range(0, len(regex)):
            if regex[i] == "'" and skip is False:
                # Special characters are delimited by ''
                skip = True
                if regex[i + 1] == "\\":
                    # Newline, tabs, etc ("\n", "\t")
                    stack.append(SymbolExpression(regex[i + 1:i + 3]))
                else:
                    # Space (" ")
                    stack.append(SymbolExpression(regex[i + 1]))
            elif regex[i] == "'" and skip is True:
                # End of special characters delimitation
                skip = False
            elif skip is True:
                continue

            elif regex[i] == "*" or regex[i] == "+" or regex[i] == "(" or regex[i] == ")" or regex[i] == "|":
                # Regex operation symbols
                stack.append(regex[i])
            else:
                # Symbol character
                stack.append(SymbolExpression(regex[i]))
            stack = reduce(stack, False)

        # Reduce stack until there is only one element in it, which
        # will be the Regular Expression
        stack = reduce(stack, True)
        # Transform regex to nfa and then to dfa
        dfas.append(nfa_to_dfa(regex_to_nfa(stack[0]), tokens[j]))
    return Lexer(dfas)


def runcompletelexer(lexer_file: str, in_file: str, out_file: str):
    lexer = read_lexer_regex(lexer_file)
    word = read_input(in_file)
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    out_f = open(out_file, "w")
    print(lexer.parse(word), file=out_f)
