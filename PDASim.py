from collections import deque
import time
import sys

import re

class PushDownAutomaton:
    def __init__(self, file_str=None):
        # internal PDA stuff (based on defn)
        self.stack = deque()
        self.state = None
        self.start_state = None
        self.input_index = 0
        self.accept_states = set()
        self.transitions = {} # (input symbol, pop symbol, push string, new state)


        # other internal vars
        self.path = None # (input symbol, pop symbol, push string, new state)
        self.is_processing = False
        self.input_str = ""

        if file_str is not None:
            with open(file_str) as f:
                isCFG = (f.readline().strip() == "CFG")
            self.parseInputFile(file_str, isCFG)

    def parseInputFile(self, file_path, isCFG):
        """Format for input files:
        First line is the input string
        Second line contains a space separated list of the different states (hopefully displayed as Latex)
        The first state in that list will be the start state
        The third line contains a space separated list of the accept states (which must be a subset of the states)
        The remaining lines are state transitions.
        A transition has the following form
        q -> p : a , b -> u
        which denotes a transition from state q to state p when input symbol a is read, b is popped off the stack,
        and u is pushed to the stack.
        a and b must be single characters. q and p must have been listed in the state list.
        Any of a, b, or u may be omitted and whitespace will be ignored

        In CFG form, the format is as follows:
        First line is the terminal alphabet separated by spaces.
        Second line is the starting nonterminal.
        Each following line contains a single rule in the following form:
        A -> u
        where u is any string of terminals and nonterminals.
        """
        with open(file_path) as f:
            if isCFG:
                f.readline()
                alphabet = [symbol.strip() for symbol in f.readline().split(" ")]
                starting_nonterminal = f.readline().strip()

                self.start_state = "q_1"
                self.accept_states = {"q_2"}
                # input, pop, push, new
                self.transitions["q_1"] = [("", "", starting_nonterminal, "q_2")]

                loops = []
                for symbol in alphabet:
                    loops.append((symbol, symbol, "", "q_2"))

                index = 3
                for line in f:
                    parts = [part.strip() for part in line.split("->")]

                    if len(parts[0]) == 0:
                        raise Exception(f'Error on line {index} of the CFG input file!  The rule {line} has no left hand side.')
                    elif len(parts[0]) > 1:
                        raise Exception(f'Error on line {index} of the CFG input file!  The rule {line} has more than one symbol on the left hand side.')

                    loops.append(("", parts[0], tuple(reversed(parts[1])), "q_2"))
                    index += 1
                self.transitions["q_2"] = loops
            else:
                states = list(state.strip() for state in f.readline().split(" "))
                self.start_state = states[0]
                self.transitions = { state: [] for state in states }

                self.accept_states = set(state.strip() for state in f.readline().split(" "))
                for a_state in self.accept_states:
                    if a_state not in states:
                        raise Exception(f'Invalid state given!  The state {a_state} was listed as an accept state, but'
                                        f' was not in the initial list of states')

                for line in f:
                    parts = [part.strip() for part in re.split("->|:|,", line)]
                    old_state = parts[0]
                    new_state = parts[1]
                    input_symbol = parts[2]
                    pop_symbol = parts[3]
                    push_string = "".join(reversed(parts[4]))

                    # check for valid format
                    if old_state not in states:
                        raise Exception(f'Invalid state given!  The state {old_state} was listed in a transition, but'
                                        f' was not in the initial list of states')
                    if new_state not in states:
                        raise Exception(f'Invalid state given!  The state {new_state} was listed in a transition, but'
                                        f' was not in the initial list of states')
                    if len(input_symbol) > 1:
                        raise Exception(f'The input symbol for a transition must have a length of 0 or 1.  The string {input_symbol} is too long.')
                    if len(pop_symbol) > 1:
                        raise Exception(f'The popped stack symbol for a transition must have a length of 0 or 1.  The string {pop_symbol} is too long.')

                    self.transitions[old_state].append((input_symbol, pop_symbol, push_string, new_state))


    def determinePath(self, input_str):
        self.input_str = input_str
        # perform a BFS to find a sequence of transitions which causes
        # the input string to be completely read, the PDA to be in an
        # accept state, and the stack to be empty
        queue = deque()
        # (location in string, current state, current stack, history of transitions)
        queue.append((0, self.start_state, deque(), deque()))
        while len(queue) != 0:
            total_state = queue.popleft()
            x = 0
            # test all possible transitions
            for trans in self.transitions[total_state[1]]:
                # check if input symbol matches and check if stack symbol matches
                if (trans[0] == "" or (total_state[0] < len(input_str) and trans[0] == input_str[total_state[0]])) and \
                    (trans[1] == "" or (len(total_state[2]) != 0 and trans[1] == total_state[2][-1])):

                    currPath = total_state[3].copy()
                    currPath.append(trans)

                    stack = total_state[2].copy()
                    if trans[1] != "":
                        stack.pop()
                    for symbol in trans[2]:
                        stack.append(symbol)

                    # we accept the string if the PDA is in an accept state, the stack is empty, and the string has been read completely
                    if trans[3] in self.accept_states and len(stack) == 0 and total_state[0] == len(input_str):
                        self.path = currPath
                        self.reset()
                        return True

                    new_state = (total_state[0]+int(trans[0] != ""), trans[3], stack, currPath)
                    queue.append(new_state)
        return False


    def transition(self):
        # (input_symbol, pop_symbol, )
        move = self.path.popleft()
        self.state = move[3]
        if move[0] != "":
            self.input_index += 1
        if move[1] != "":
            self.stack.pop()
        if move[2] != "":
            for char in move[2]:
                self.stack.append(char)
        if len(self.path) == 0:
            self.is_processing = False

    def reset(self):
        self.input_index = 0
        self.state = self.start_state
        self.is_processing = True

    def printTotalState(self, input_str):
        print(f'Current State: {self.state}')
        print(" "*self.input_index+"v")
        print(input_str)
        print(f'Stack: {"".join(self.stack)}')
        print()


    def runAcceptOnString(self, input_str):
        found_path = self.determinePath(input_str)
        if not found_path:
            print("String is not accepted.")
            return
        else:
            self.printTotalState(input_str)
            while self.is_processing:
                self.transition()
                self.printTotalState(input_str)
                time.sleep(1)

    @staticmethod
    def convertToC(PDA):
        CPDA = PushDownAutomaton()
        CPDA.start_state = PDA.start_state
        CPDA.accept_states = PDA.accept_states.copy()

        for old in PDA.transitions:
            CPDA.transitions[old] = []

        # input, pop, push, new
        for old, transitions in PDA.transitions.items():
            for trans in transitions:
                # exactly one of the push/pop is empty
                if (len(trans[1]) == 1 and trans[2] == "") or \
                    (trans[1] == "" and len(trans[2]) == 1):
                    CPDA.transitions[old].append(trans)
                # both push and pop are empty
                elif len(trans[1]) == 0 and len(trans[2]) == 0:
                    intermediate_state = old+"empty"+trans[3]
                    if intermediate_state in CPDA.transitions:
                        raise Exception("Okay, really!?!  What kind of weird state naming convention are you using!!  I give up.  I can't convert this to a CFG.")
                    CPDA.transitions[old].append((trans[0], "", "c", intermediate_state))
                    CPDA.transitions[intermediate_state] = [("", "c", "", trans[3])]
                # neither push nor pop is empty
                else:
                    inter_states = [old+symbol+str(index)+trans[3] for index, symbol in enumerate(trans[2])]
                    inter_states.append(trans[3])
                    for index, inter_state in enumerate(inter_states[:-1]):
                        if inter_state in CPDA.transitions:
                            raise Exception("Okay, really!?!  What kind of weird state naming convention are you using!!  Convert this yourself!")
                        CPDA.transitions[inter_state] = [("", "", trans[2][index], inter_states[index+1])]

                    CPDA.transitions[old].append((trans[0], trans[1], "", inter_states[0]))

        return CPDA

    @staticmethod
    def convertToCFG(PDA):
        rules = []
        CPDA = PushDownAutomaton.convertToC(PDA)

        states = set(CPDA.transitions.keys())
        states.union(trans[3] for transitions in CPDA.transitions.values() for trans in transitions)

        start_sym = "S"
        if "S" in states:
            start_sym = "S_0"

        for end_state in states:
            dest_trans = []
            for old, transitions in CPDA.transitions.items():
                for trans in transitions:
                    if trans[3] == end_state and len(trans[1]) == 1:
                        dest_trans.append((old, trans))
            for not_end_state, dest_tran in dest_trans:
                for start_state in states:
                    for trans in CPDA.transitions[start_state]:
                        if dest_tran[1] == trans[2]:
                            rules.append(f'A_{{{start_state},{end_state}}} -> {trans[0]}A_{{{trans[3]},{not_end_state}}}{dest_tran[0]}')


        for a_state in CPDA.accept_states:
            rules.append(f'{start_sym} -> A_{{{CPDA.start_state},{a_state}}}')

        for state in states:
            rules.append(f'A_{{{state},{state}}} -> ')

        for state1 in states:
            for state2 in states:
                for state3 in states:
                    rules.append(f'A_{{{state1},{state2}}} -> A_{{{state1},{state3}}}A_{{{state3},{state2}}}')

        return rules

# format for args is
# file_name input_str
# file_name -c
file = sys.argv[1]
PDA = PushDownAutomaton(file)
if len(sys.argv) >= 3 and sys.argv[2] == "-c":
    cfgRules = PushDownAutomaton.convertToCFG(PDA)
    for rule in cfgRules:
        print(rule)
elif len(sys.argv) >= 3:
    PDA.runAcceptOnString(sys.argv[2])
else:
    PDA.runAcceptOnString("")