# Formal-Languages-and-Automata
## Project: Lexer Implementation in Python
The project was divided into three main stages:
1. Lexer that takes Deterministic Finite Automata as input  
A DFA is composed of: an alphabet, a set of states, an initial state, transition function, a set of accepting states. The DFAs can also have a token for readability.  
The Lexer is a list of DFAs.  
The Lexer receieves as input a list of DFAs and a word and outputs the lexemes generated with the token of the DFA that accepted the respective lexeme.
2. Regex to NFA Transformation, NFA to DFA Transformation  
The program receives as input Regexes in Prenex Form and transforms the given Regex firstly to an NFA using Thomson's construction algorithm, then transforms the NFA to the corresponding DFA using the Subset Construction Algorithm and outputs this DFA.
3. Lexer that takes Regex as input  
The Lexer receives as input a list of Regexes with their corresponding tokens instead of a list of DFAs, and a word and outputs the lexemes generated with the token of the DFA that accepted the respective lexeme.  
The Regexes have to be parsed first so that they can be transformed into a NFA than into a DFA in order for the Lexer to split the word into lexemes. 
