#!/usr/bin/env python3
""" Data Structures and Algorithms for CL III, Project 1
    See <https://dsacl3-2019.github.io/p1/> for detailed instructions.
    Authors:      Giulio Cusenza, Darja Jepifanova
    Honor Code:  We pledge that this program represents our own work.
    We received help from nobody
"""


class FSA:
    """ A class representing finite state automata.
    Args:
        deterministic: The automaton is deterministic
    Attributes:
        transitions: transitions kept as a dictionary
            where keys are the tuple (source_state, symbol),
            values are the target state for DFA
            and a set of target states for NFA.
            Note that we do not require a dedicated 'sink' state.
            Any undefined transition should cause the FSA to reject the
            string immediately.
        start_state: number/name of the start state
        accepting: the set of accepting states
        is_deterministic (boolean): whether the FSA is deterministic or not
    """

    def __init__(self, deterministic=True):
        self.transitions = dict()
        self.start_state = None
        self.accepting = set()
        self.is_deterministic = deterministic
        self._alphabet = set()  # just for convenience, we can
        self._states = set()  # always read it off from transitions

    def add_transition(self, s1, sym, s2=None, accepting=False):
        """ Add a transition from state s1 to s2 with symbol
        """
        if self.start_state is None:
            self.start_state = s1
            self._states.add(s1)
        if s2 is None:
            s2 = len(self._states)
            while s2 in self._states: s2 += 1
        self._states.add(s1)
        self._states.add(s2)
        self._alphabet.add(sym)
        if (s1, sym) not in self.transitions:
            self.transitions[(s1, sym)] = set()
        self.transitions[(s1, sym)].add(s2)
        if accepting:
            self.accepting.add(s2)
        if len(self.transitions[(s1, sym)]) > 1:
            self.is_deterministic = False
        return s2

    def mark_accept(self, state):
        self.accepting.add(state)

    def is_accepting(self, state):
        return state in self.accepting

    def move(self, sym, s1=None):
        """ Return the state(s) reachable from 's1' on 'symbol'
        """
        if s1 is None: s1 = self.start_state
        if (s1, sym) not in self.transitions:
            return set()
        else:
            return self.transitions[(s1, sym)]

    def _recognize_dfa(self, s):
        state = self.start_state
        for sym in s:
            states = self.transitions.get((state, sym), None)
            if states is None:
                return False
            else:
                state = next(iter(states))
        if state in self.accepting:
            return True
        else:
            return False

    def _recognize_nfa(self, s):
        """ NFA recognition of 's' using a stack-based agenda.
        """
        agenda = []
        inp_pos = 0
        for node in self.transitions.get((self.start_state, s[inp_pos]), []):
            agenda.append((node, inp_pos + 1))
        while agenda:
            node, inp_pos = agenda.pop()
            if inp_pos == len(s):
                if node in self.accepting:
                    return True
            else:
                for node in self.transitions.get((node, s[inp_pos]), []):
                    agenda.append((node, inp_pos + 1))
        return False

    def recognize(self, s):
        """ Recognize the given string 's', return a boolean value
        """
        if self.is_deterministic:
            return self._recognize_dfa(s)
        else:
            return self._recognize_nfa(s)

    @staticmethod
    def _get_set_id(s, transitions, subset_of):
        return tuple(sorted([(k, subset_of[v]) for k, v in transitions[s].items()], key=lambda x: x[0]))

    @staticmethod
    def _get_state_subset_dict(partition):
        subset_of = dict()
        for i, subset in enumerate(partition):
            for state in subset:
                subset_of.update({state: i})
        return subset_of

    def minimize(self):
        """
        Minimize DFA.
        """
        # Construct new transition dictionary of shape {s1: {sym: s2}}
        transitions = dict()
        for s1, sym in self.transitions:
            s2 = next(iter(self.move(sym, s1)))  # we assume determinism (i.e. only one s2)
            if s1 not in transitions:
                transitions.update({s1: {sym: s2}})
            if s1 in transitions:
                transitions[s1].update({sym: s2})
        for leftover_state in self._states - set(transitions.keys()):
            transitions.update({leftover_state: dict()})

        # Iteratively find partition
        partition = list()
        new_partition = [self._states - self.accepting, self.accepting]
        while len(new_partition) != len(partition):
            # Update iteration variable
            partition = new_partition
            new_partition = list()
            subset_of = FSA._get_state_subset_dict(partition)
            # Partition subset into its subsets based on the right language of the states
            for subset in partition:
                subsubsets = dict()
                for s in subset:
                    set_id = FSA._get_set_id(s, transitions, subset_of)
                    if set_id not in subsubsets:
                        subsubsets.update({set_id: [s]})
                    else:
                        subsubsets[set_id].append(s)
                # Add new sets to new partition
                for new_subset in subsubsets.values():
                    new_partition.append(set(new_subset))

        # Merge equal states
        subset_of = FSA._get_state_subset_dict(partition)
        minimised_fsa = FSA()
        minimised_fsa.start_state = self.start_state
        for s1, sym in self.transitions:
            s2 = next(iter(self.move(sym, s1)))
            accepting = s2 in self.accepting
            minimised_fsa.add_transition(subset_of[s1], sym, subset_of[s2], accepting)

        # Update instance object
        self.__dict__ = minimised_fsa.__dict__


def build_trie(words: list) -> FSA:
    """Given a list of words, create and return a trie FSA.
    For the given sequence of words, you should build a trie,
    an FSA where letters are the edge labels. Since the structure is a
    trie, common prefix paths should be shared but suffixes will
    necessarily use many redundant paths.
    You should initialize an instance of the FSA class defined above,
    and add only the required arcs successively. 
    """
    fsa = FSA(deterministic=True)
    fsa.start_state = 0
    fsa._states.add(fsa.start_state)

    # Add transitions for each word
    for word in words:
        current_state = fsa.start_state
        for char in word:
            next_state = None
            for state in fsa.transitions.get((current_state, char), []):
                if next_state is None:
                    next_state = state
                else:
                    # Non-deterministic transition
                    fsa.is_deterministic = False
                    next_state = fsa.add_transition(current_state, char)
                    fsa.add_transition(next_state, char, state)
            if next_state is None:
                # create a new state
                next_state = fsa.add_transition(current_state, char)
            current_state = next_state

        # mark the final state  as accepting
        fsa.accepting.add(current_state)

    return fsa


if __name__ == '__main__':
    """
    # Example usage:
    m = build_trie(["walk", "walks", "wall", "walls", "want", "wants",
                    "work", "works", "forks"])
    m.minimize()
    assert m.recognize("walk") == True
    assert m.recognize("wark") == False
    print("\nExample:")
    print(m.start_state, m.accepting)
    for t in m.transitions.items():
        print(t)

    # Test 1:
    test1 = build_trie(["walk", "wall", "talk", "tall"])
    test1.minimize()
    print("\n\nTest 1:")
    print(test1.start_state, test1.accepting)
    print(test1.transitions)
    """
    # Test 2:
    test2 = build_trie(["ace", "ice"])
    test2.minimize()
    print("\n\nTest 2:")
    print(test2.start_state, test2.accepting)
    print(test2.transitions)

    # Test lexicon:
    with open('lexicon.txt', 'rt') as f:
        words = f.read().strip().split()
    lexicon = build_trie(words)
    print("\n\nLexicon test:")
    print("- previous -")
    print("| n states:", len(lexicon._states))
    print("| start state:", lexicon.start_state)
    print("| n accepting:", len(lexicon.accepting))
    print("| n transitions:", len(lexicon.transitions))
    lexicon.minimize()
    print("- minimised -")
    print("| n states:", len(lexicon._states))
    print("| start state:", lexicon.start_state)
    print("| n accepting:", len(lexicon.accepting))
    print("| n transitions:", len(lexicon.transitions))
