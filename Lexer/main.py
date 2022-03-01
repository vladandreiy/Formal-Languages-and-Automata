from typing import *
from Lexer import FiniteAutomata, State
from expression import *
import sys
import os


# Returns the epsilon closure for a given state in a nfa
def epsilon_closure(nfa, state: int) -> Set[int]:
    states = set()
    states.add(state)
    index = 1
    while True:
        accessible_states = []
        for i in k_next_conf_nfa(nfa, (state, ""), index):
            accessible_states.append(i[0])
        if set(accessible_states).issubset(states):
            break
        states = states.union(set(accessible_states))
        index += 1
    return states


# Returns a list of next possible configurations from a given configuration
def next_conf_nfa(nfa, conf):
    state = conf[0]
    word = conf[1]
    conf_l = []
    for transition in nfa.delta:
        if state == transition.curr_state:
            if transition.character == "epsilon":
                conf_l.append((transition.next_state, word))
            if transition.character not in nfa.alphabet or word == "":
                continue
            if transition.character == word[0]:
                conf_l.append((transition.next_state, word[1:]))
            if transition.character == word[0:2]:
                conf_l.append((transition.next_state, word[2:]))
    return conf_l


# Returns the configurations that can be reached in k steps
def k_next_conf_nfa(nfa, conf, k):
    conf_prev = next_conf_nfa(nfa, conf)
    for i in range(k - 1):
        conf_next = []
        for conf in conf_prev:
            conf_next.extend(next_conf_nfa(nfa, conf))
        conf_prev = conf_next
    return conf_prev


class StateSet:
    def __init__(self, curr_state: frozenset, character: str, next_state: frozenset):
        self.curr_state = curr_state
        self.character = character
        self.next_state = next_state

    def __str__(self):
        string = str(self.curr_state) + " '" + self.character + "' " + str(self.next_state)
        return string


# Converts a NFA to a DFA using Subset Construction Algorithm
def nfa_to_dfa(nfa: FiniteAutomata, token=""):
    # A state in the dfa: set(0, 1, 2) => a set of states from the nfa
    dfa_states = []
    dfa_delta = []

    # Generate epsilon closure for each state in the nfa
    epsilon_closures = []
    for i in range(nfa.final_states + 1):
        epsilon_closures.append(epsilon_closure(nfa, i))

    # The initial state in the dfa is the epsilon closure of the initial state of the nfa
    dfa_initial_state = frozenset(epsilon_closures[nfa.initial_state])
    dfa_states.append(dfa_initial_state)

    # For each state in the dfa
    for dfa_state in dfa_states:
        # For each symbol in the alphabet, get the transitions 
        for symbol in nfa.alphabet:
            new_state = set()
            # A state in the dfa is a set of states from the nfa
            # Get all transitions from each state in the nfa on current symbol
            for nfa_state in dfa_state:
                conf_list = next_conf_nfa(nfa, (nfa_state, symbol))
                for conf in conf_list:
                    if conf[1] == '':
                        new_state = new_state.union(epsilon_closures[conf[0]])
            new_state = frozenset(new_state)
            # If generated state is not in dfa_states, add it
            if new_state not in dfa_states:
                dfa_states.append(new_state)
            # Add transition in delta function
            dfa_delta.append(StateSet(dfa_state, symbol, new_state))

    # Refactor states in dfa to be ints instead of sets
    dfa_states_dict = dict()
    index = 0
    new_final_states = []
    for dfa_state in dfa_states:
        dfa_states_dict[dfa_state] = str(index)
        # If the set of states from the dfa contains the final state from the nfa
        # It is a final state in the dfa
        if any(state == nfa.final_states for state in dfa_state):
            new_final_states.append(index)
        index += 1

    new_initial_state = dfa_states_dict[dfa_initial_state]
    new_dfa_delta = []
    for dfa_trans in dfa_delta:
        new_dfa_delta.append(
            State(dfa_states_dict[dfa_trans.curr_state],
                  dfa_trans.character,
                  dfa_states_dict[dfa_trans.next_state]))

    # Sink State
    sink_state = index
    no_transition_dict = dict()
    for trans in new_dfa_delta:
        if trans.curr_state not in no_transition_dict:
            no_transition_dict[trans.curr_state] = [trans.character]
        else:
            no_transition_dict[trans.curr_state].append(trans.character)

    # Add missing transitions, if there are any
    if not all(len(no_transition_dict[key]) == len(nfa.alphabet) for key in no_transition_dict.keys()):
        for letter in nfa.alphabet:
            for i in range(0, sink_state + 1):
                if str(i) not in no_transition_dict or letter not in no_transition_dict[str(i)]:
                    new_dfa_delta.append(State(str(i), letter, str(sink_state)))

    return FiniteAutomata(nfa.alphabet, new_dfa_delta, new_initial_state, new_final_states, token)


# Regex to NFA conversion using Thomson's algorithm
def regex_to_nfa(expr: Expression) -> FiniteAutomata:
    index = 0
    (nfa, index) = regex_to_nfa_recursive(expr, index)
    return nfa


def regex_to_nfa_recursive(expr: Expression, index: int) -> (FiniteAutomata, int):
    if issubclass(type(expr), SymbolExpression):
        initial_state = index
        index += 1
        final_state = index
        index += 1
        alphabet = set()
        alphabet.add(expr.char)
        delta = [State(initial_state, expr.char, final_state)]
        nfa = FiniteAutomata(alphabet, delta, initial_state, final_state)
        return nfa, index

    if issubclass(type(expr), ConcatenationExpression):
        (nfa1, index) = regex_to_nfa_recursive(expr.expr1, index)
        (nfa2, index) = regex_to_nfa_recursive(expr.expr2, index)
        alphabet = nfa1.alphabet.union(nfa2.alphabet)
        initial_state = nfa1.initial_state
        final_state = nfa2.final_states
        delta = nfa1.delta
        delta.extend(nfa2.delta)
        delta.append(State(nfa1.final_states, "epsilon", nfa2.initial_state))
        nfa = FiniteAutomata(alphabet, delta, initial_state, final_state)
        return nfa, index

    if issubclass(type(expr), UnionExpression):
        (nfa1, index) = regex_to_nfa_recursive(expr.expr1, index)
        (nfa2, index) = regex_to_nfa_recursive(expr.expr2, index)
        alphabet = nfa1.alphabet.union(nfa2.alphabet)
        initial_state = index
        index += 1
        final_state = index
        index += 1
        delta = nfa1.delta
        delta.extend(nfa2.delta)
        delta.append(State(initial_state, "epsilon", nfa1.initial_state))
        delta.append(State(initial_state, "epsilon", nfa2.initial_state))
        delta.append(State(nfa1.final_states, "epsilon", final_state))
        delta.append(State(nfa2.final_states, "epsilon", final_state))
        nfa = FiniteAutomata(alphabet, delta, initial_state, final_state)
        return nfa, index

    if issubclass(type(expr), StarExpression):
        (nfa, index) = regex_to_nfa_recursive(expr.expr, index)
        alphabet = nfa.alphabet
        initial_state = index
        index += 1
        final_state = index
        index += 1
        delta = nfa.delta
        delta.append(State(initial_state, "epsilon", nfa.initial_state))
        delta.append(State(nfa.final_states, "epsilon", final_state))
        delta.append(State(nfa.final_states, "epsilon", nfa.initial_state))
        delta.append(State(initial_state, "epsilon", final_state))
        nfa = FiniteAutomata(alphabet, delta, initial_state, final_state)
        return nfa, index
    
    if issubclass(type(expr), PlusExpression):
        (nfa, index) = regex_to_nfa_recursive(ConcatenationExpression(expr.expr, StarExpression(expr.expr)), index)
        return nfa, index


if __name__ == '__main__':
    args = sys.argv[1:]
    input_filename = args[0]
    output_filename = args[1]
    with open(input_filename) as input_file:
        line = input_file.readline()
        dfa = nfa_to_dfa(regex_to_nfa(create_expr(line)))
        os.makedirs(os.path.dirname(output_filename), exist_ok=True)
        output_file = open(output_filename, "w")
        print(dfa, file=output_file)
