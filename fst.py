#!/usr/bin/env python3
""" Data Structures and Algorithms for CL III, Project 1
    See <https://dsacl3-2019.github.io/p1/> for detailed instructions.
    Authors:      Giulio Cusenza, Darja Jepifanova
    Honor Code:  We pledge that this program represents our own work.
    We received help from nobody
"""
from fsa import FSA
from fsa import build_trie


class FST:
    """
    A weighted FST class.
    """

    def __init__(self):
        self.transitions = dict()
        self.start_state = None
        self.accepting = set()
        self._sigma_in = set()
        self._sigma_out = set()
        self._states = {0}

    @classmethod
    def fromfsa(cls, fsa: FSA):
        """Return an FST instance using an FSA.

        This method should take an instance of the FSA class defined
        in fsa.py, and returns an FST with identity transitions.
        """
        fst = cls()
        for (s1, sym), s2s in fsa.transitions.items():
            for s2 in s2s:
                fst.add_transition(s1, sym, s2, sym)
        fst.accepting = fsa.accepting
        fst.start_state = fsa.start_state
        return fst

    def mark_accepting(self, state):
        self.accepting.add(state)

    def get_transitions(self, s1, insym=None):
        """
        """
        if insym is None:
            syms = self._sigma_in
        else:
            syms = (insym,)
        for sym in syms:
            if (s1, sym) in self.transitions:
                for outsym, s2, w in self.transitions[(s1, sym)]:
                    yield s2, outsym, w

    def add_transition(self, s1, insym, s2=None, outsym=None, w=0, accepting=False):
        """Add a transition from s1 to s2 with label insym:outsym.

        If s2 is None, create a new state. If outsym is None, assume
        identity transition.

        We assume transition labels are characters, and the states are
        integers, and we use integer labels when we create states.
        However, the code should (mostly) work fine with arbitrary labels.
        """
        if self.start_state is None:
            self.start_state = s1
            self._states.add(s1)
        if s2 is None:
            s2 = len(self._states)
            while s2 in self._states: s2 += 1
        if s2 not in self._states:
            self._states.add(s2)
        if outsym is None: outsym = insym
        self._sigma_in.add(insym)
        self._sigma_out.add(outsym)
        if (s1, insym) not in self.transitions:
            self.transitions[(s1, insym)] = set()
        self.transitions[s1, insym].add((outsym, s2, w))
        if accepting:
            self.accepting.add(s2)
        return s2

    def move(self, s1, insym):
        """ Return the state(s) reachable from 's1' on 'symbol'
        """
        if (s1, insym) in self.transitions:
            return self.transitions[(s1, insym)]
        else:
            return set()

    def transduce(self, s):
        # define a class Path
        class Path:
            def __init__(self, current_state=0, string="", weight=0, input_pos=0, is_accepting=False):
                self.current_state = current_state
                self.string = string
                self.weight = weight
                self.input_pos = input_pos  # pos of next letter to read in s
                self.is_accepting = is_accepting

        # add all the transitions from the initial state transitioning on the first letter
        paths = set()
        # add paths for transitions on s[0]
        for outsym, state, w in self.transitions.get((self.start_state, s[0]), []):
            accepting = state in self.accepting
            paths.add(Path(state, outsym, w, 1, accepting))
        # add paths for transitions on epsilon
        for outsym, state, w in self.transitions.get((self.start_state, ""), []):
            accepting = state in self.accepting
            paths.add(Path(state, outsym, w, 0, accepting))  # input_pos does not increase on epsilon transitions

        # transduce
        accepting_strings = set()
        while paths:
            new_paths = set()
            for path in paths.copy():
                # remove path that reached the end of the string
                if path.input_pos == len(s):
                    paths -= {path}
                    # yield its string and respective weight if its last state was accepting
                    if path.is_accepting:
                        accepting_strings.add((path.string, path.weight))

                # follow path further
                elif path.input_pos < len(s):
                    # add new paths for transitions on the next letter of s
                    for outsym, state, w in self.transitions.get((path.current_state, s[path.input_pos]), []):
                        string = path.string + outsym
                        total_weight = path.weight + w
                        input_pos = path.input_pos + 1
                        accepting = state in self.accepting
                        new_paths.add(Path(state, string, total_weight, input_pos, accepting))
                    # add new paths for transitions on epsilon
                    for outsym, state, w in self.transitions.get((path.current_state, ""), []):
                        # save new paths (the old path may branch out)
                        string = path.string + outsym
                        total_weight = path.weight + w
                        input_pos = path.input_pos  # do not increase input_pos on epsilon transitions
                        accepting = state in self.accepting
                        new_paths.add(Path(state, string, total_weight, input_pos, accepting))
                    # remove old path
                    paths -= {path}

            # union (for next iteration)
            paths = paths.union(new_paths)

        return accepting_strings

    def invert(self):
        """
        Invert the FST.
        """
        inverted = FST()
        for s1, insym in self.transitions:
            for s2, outsym, w in self.get_transitions(s1, insym):
                inverted.add_transition(s1, outsym, s2, insym, w)
        inverted.accepting = self.accepting
        inverted.start_state = self.start_state

        self.__dict__ = inverted.__dict__

    @staticmethod
    def _cross(s1: set, s2: set):
        """
        Return the cross product of two sets.
        """
        cross_set = set()
        for e1 in s1:
            for e2 in s2:
                cross_set.add((e1, e2))
        return cross_set

    @classmethod
    def compose_fst(cls, m1, m2):
        """
        Compose two FST instances (m1 and m2) and return the composed FST.

        While implementing this method, you should pay attention to
        epsilons, since our use case requires epsilon transitions.
        However, you can make use of the fact that `m1` does not
        include any epsilon transitions in our application. Also,
        since `m1` in our application is not weighted, the arc weight
        can trivially be taken from `m2`.
        """
        composed_fst = FST()

        # Set initial and final states
        composed_fst.start_state = (0, 0)
        composed_fst.accepting = cls._cross(m1.accepting, m2.accepting)

        # Add epsilon transitions to m1
        for state in m1._states:
            m1.add_transition(state, "", state)

        # Combine transition rules
        for from_state1, insym1 in m1.transitions:
            for to_state1, outsym1, _ in m1.get_transitions(from_state1, insym1):
                for from_state2, insym2 in m2.transitions:
                    if outsym1 == insym2:
                        for to_state2, outsym2, w in m2.get_transitions(from_state2, insym2):
                            s1 = (from_state1, from_state2)
                            s2 = (to_state1, to_state2)
                            composed_fst.add_transition(s1, insym1, s2, outsym2, w)

        # Find reachable states
        visited = {composed_fst.start_state}
        queue = [composed_fst.start_state]
        while queue:
            s1 = queue.pop()
            for insym in composed_fst._sigma_in:
                for s2, _, w in composed_fst.get_transitions(s1, insym):
                    if s2 not in visited:
                        queue.append(s2)
                        visited.add(s2)

        # Remove unreachable states
        composed_fst._states = visited.union({composed_fst.start_state})
        composed_fst.accepting = composed_fst.accepting.intersection(visited)
        for s1, insym in composed_fst.transitions.copy():
            if s1 not in visited:
                composed_fst.transitions.pop((s1, insym))

        # Return composed FST
        return composed_fst


if __name__ == "__main__":

    lexicon1 = ["walk", "walks", "wall", "walls", "want", "wants", "work", "works", "forks"]
    lexicon2 = ["walk", "wall", "talk", "tall"]
    lexicon3 = ["walk", "walks"]
    fsa = build_trie(lexicon1)
    fsa.minimize()
    print("\nFSA:")
    for t in fsa.transitions.items():
        print(t)

    print("\nFST from FSA:")
    fst = FST.fromfsa(fsa)
    for t in fst.transitions.items():
        print(t)

    print("\nTransduce \"walk\":")
    print(fst.transduce("walk"))

    print("\n-------------------------")

    a = FST()
    a.add_transition(0, "a", 0, "f", 5)
    a.add_transition(0, "d", 2, "f", 3, True)
    a.add_transition(0, "a", 1, "b", 1)
    a.add_transition(1, "a", 2, "c", 2, True)
    a.add_transition(1, "d", 2, "e", 3, True)

    print("\nOriginal:")
    for t in a.transitions.items():
        print(t)

    print("\nTransduce \"ad\":")
    c = a.transduce("ad")
    print(c)

    print("\nInverted:")
    a.invert()
    for t in a.transitions.items():
        print(t)

    print("\n-------------------------")

    print("\nFST 1:")
    m1 = FST()
    m1.accepting = {2}
    m1.add_transition(0, "a", 1, "b")
    m1.add_transition(1, "a", 1)
    m1.add_transition(1, "b", 1)
    m1.add_transition(1, "a", 2, "b")
    for t in m1.transitions.items():
        print(t)
    print("\nFST 2:")
    m2 = FST()
    m2.accepting = {0, 1}
    m2.add_transition(0, "b", 0)
    m2.add_transition(0, "c", 0)
    m2.add_transition(0, "a", 1)
    m2.add_transition(1, "a", 1)
    m2.add_transition(1, "c", 0)
    m2.add_transition(1, "b", 0, "c")
    for t in m2.transitions.items():
        print(t)

    print("\nExpected composed FST:")
    expected_m3 = FST()
    expected_m3._states = set()
    expected_m3.accepting = {(2, 0)}
    expected_m3.add_transition((0, 0), "a", (1, 0), "b")
    expected_m3.add_transition((1, 0), "b", (1, 0))
    expected_m3.add_transition((1, 0), "a", (1, 1))
    expected_m3.add_transition((1, 0), "a", (2, 0), "b")
    expected_m3.add_transition((1, 1), "a", (1, 1))
    expected_m3.add_transition((1, 1), "b", (1, 0), "c")
    expected_m3.add_transition((1, 1), "a", (2, 0), "c")
    print("states: " + str(expected_m3._states))
    print("accepting: " + str(expected_m3.accepting))
    for t in sorted(expected_m3.transitions.items()):
        print(t)

    print("\nComposed FST:")
    m3 = FST.compose_fst(m1, m2)
    print("states: " + str(m3._states))
    print("accepting: " + str(m3.accepting))
    for t in sorted(m3.transitions.items()):
        print(t)

    print("\nTransduced composed FSTs:")
    print(m3.transduce("aba"))
