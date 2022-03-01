import os


class State:
    def __init__(self, curr_state: str, character: str, next_state: str):
        self.curr_state = curr_state
        self.character = character
        self.next_state = next_state

    def __str__(self):
        string = str(self.curr_state) + " '" + self.character + "' " + str(self.next_state)
        return string

    def __lt__(self, other):
        return (int(self.curr_state), self.character, int(self.next_state)) < \
               (int(other.curr_state), other.character, int(other.next_state))

    def __eq__(self, other):
        return (int(self.curr_state), self.character, int(self.next_state)) == \
               (int(other.curr_state), other.character, int(other.next_state))


class FiniteAutomata:
    def __init__(self, alphabet, delta, initial_state, final_states, token=""):
        self.alphabet = alphabet
        self.delta = delta
        self.initial_state = initial_state
        self.final_states = final_states
        self.token = token

    def next_conf(self, conf):
        state = conf[0]
        word = conf[1]
        next_state = 0
        found_transition = False
        for transition in self.delta:
            if transition.character not in self.alphabet:
                return next_state, word, False
            if state == transition.curr_state and transition.character == "\\n" and word[0] == "\n":
                next_state = transition.next_state
                found_transition = True
                word = word[1:]
                break
            if state == transition.curr_state and transition.character == word[0]:
                next_state = transition.next_state
                found_transition = True
                word = word[1:]
                break
        return next_state, word, found_transition

    def accept_word(self, word):
        state = self.initial_state
        while len(word) > 0:
            (state, word, found_transition) = self.next_conf((state, word))
            if not found_transition:
                return False
        if int(state) in self.final_states:
            return True
        else:
            return False

    def __str__(self):
        s = str()
        s += self.token + "\n"
        for letter in sorted(self.alphabet):
            s += letter
        trans_string = str()
        states_set = set()
        for trans in sorted(self.delta):
            trans_string += str(trans.curr_state) + ",\'" + str(trans.character) + "\'," + str(trans.next_state) + "\n"
            states_set.add(trans.curr_state)
            states_set.add(trans.next_state)
        s += "\n" + str(len(states_set)) + "\n" + str(self.initial_state) + "\n"
        if isinstance(self.final_states, int):
            s += str(self.final_states)
        else:
            for i in range(len(self.final_states)):
                s += str(self.final_states[i]) + " "
        s += "\n" + trans_string.rstrip()
        return s


class Lexer:
    def __init__(self, dfas):
        self.dfas = dfas

    def longest_prefix(self, word):
        prefixes = [0] * len(self.dfas)
        for i in range(1, len(word) + 1):
            for j in range(0, len(self.dfas)):
                if self.dfas[j].accept_word(word[:i]):
                    prefixes[j] = i
        max_length = max(prefixes)
        index = prefixes.index(max_length)
        return index, max_length

    def parse(self, word):
        res = ""
        original_word = word
        while len(word) > 0:
            prev_word = word
            (index, max_length) = self.longest_prefix(word)
            lexeme = word[:max_length]
            word = word[max_length:]
            if lexeme == "\n":
                lexeme = "\\n"
            res += self.dfas[index].token + " " + lexeme + "\n"
            if len(word) > 0 and word[0] != "\n" and not any(word[0] in dfa.alphabet for dfa in self.dfas):
                return "No viable alternative at character " + str(original_word.find(word)) + ", line 0"
            if word == prev_word:
                if original_word.rfind(word) == len(original_word) - 1:
                    return "No viable alternative at character EOF, line 0"
                return "No viable alternative at character " + str(original_word.find(word) + 1) + ", line 0"
        res = res[:-1]
        return res

    def __str__(self):
        string = ""
        for dfa in self.dfas:
            string += str(dfa) + "\n"
        return string


def read_input(input_filename: str) -> str:
    with open(input_filename) as input_file:
        return input_file.read()


def dfa_indices(s):
    indices = [-2]
    for i in range(0, len(s)):
        if s[i] == "\n":
            indices.append(i - 1)
    indices.append(len(s) - 1)
    return indices


def get_alphabet(s: str):
    alphabet = set()
    skip = False
    for i in range(0, len(s)):
        if s[i] == "\\" and i < len(s) - 1 and s[i + 1] == "n":
            alphabet.add("\\n")
            skip = True
        elif skip:
            skip = False
            continue
        else:
            alphabet.add(s[i])
    return alphabet


def read_lexer(lexer_file: str):
    dfas = []
    with open(lexer_file) as input_file:
        lines = input_file.readlines()
        indices = dfa_indices(lines)
        for i in range(len(indices) - 1):
            start = indices[i] + 2
            end = indices[i + 1]
            alphabet = get_alphabet(lines[start][:-1])
            token = lines[start + 1].rstrip()
            initial_state = int(lines[start + 2].rstrip())
            states = []
            for k in range(start + 3, end):
                transition = lines[k].rstrip().split(",")
                states.append(State(int(transition[0]), transition[1].strip("'"), int(transition[2])))
            final_states = list(map(int, (lines[end]).split()))
            dfa = FiniteAutomata(alphabet, states, initial_state, final_states, token)
            dfas.append(dfa)
    return Lexer(dfas)


def runlexer(lexer_file: str, in_file: str, out_file: str):
    lexer = read_lexer(lexer_file)
    word = read_input(in_file)
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    out_f = open(out_file, "w")
    print(lexer.parse(word), file=out_f)
