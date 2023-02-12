from collections import deque

from manim import *
import re

class PushDownAutomatonViewer(Scene):
    def construct(self):
        pda = PushDownAutomaton("TestPDA.txt")
        # draw state diagram?
        pda.determinePath()
        while pda.is_processing:
            pda.transition()
            # update scene

class PushDownAutomaton:
    def __init__(self, file_str):
        # internal PDA stuff (based on defn)
        self.stack = deque()
        self.state = "q_0"
        self.input_index = 0
        self.accept_states = set()

        # other internal vars
        self.input_str = ""
        self.is_processing = False
        self.transitions = {}

        # (input symbol, pop symbol, push string, new state)
        self.path = deque()

        self.parseInputFile(file_str)

    def parseInputFile(self, file_path):
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
        """
        with open(file_path) as f:
            self.input_str = f.readline()

            states = set(state.strip() for state in f.readline().split(" "))
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
                push_string = parts[4]

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


    def determinePath(self):
        # perform a BFS to find a sequence of transitions which causes
        # the input string to be completely read, the PDA to be in an
        # accept state, and the stack to be empty
        pass

    def transition(self):
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


