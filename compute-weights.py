#!/usr/bin/env python3
"""
Data Structures and Algorithms for CL 3, Project 1
See <https://https://dsacl3-2022.github.io/p1/> for detailed instructions.
Authors:      Giulio Cusenza, Darja Jepifanova
Honor Code:  We pledge that this program represents our own work.
We received help from nobody
"""

import numpy as np


def cost(ch1: str, ch2: str, counts: dict = None):
    """ Given two aligned characters, return cost for ch1 -> ch2.

    This function should be called from the find_edits() function
    below when calculating costs for the edit operations.  If the
    first character is the empty string, it indicates an insert.
    Similarly, an empty string as the second character indicates a
    deletion.

    If `counts` is not given, the function should return 1 for all
    operations. if `counts` is given, you are strongly recommended to
    use estimated probability p of the edit operation from the given
    counts, and return `1 - p` as the cost (you should also consider
    using a smoothing technique). You are also welcome to 
    experiment with other scoring functions.

    """
    if ch1 == ch2:  # XXX should we really have cost 0 on char equality?
        # cost = 0
        return 0
    elif counts:
        # cost = 1 - probability of the operation with Laplace smoothing
        return 1 - (counts[ch1][ch2] + 1) / (sum(counts[ch1].values()) + len(counts[ch1]))
    else:
        # cost = 1
        return 1


def find_edits(s1: str, s2: str, counts: dict = None) -> list:
    """ Find edits with minimum cost for given sequences.

    This function should implement the edit distance algorithm, using
    the scoring function above. If `counts` is given, the scoring
    should be based on the counts edits passed.

    The return value from this function should be a list of tuples.
    For example if the best alignment between correct word `work` and
    the misspelling `wrok` is as follows

                        wor-k
                        w-rok

    the return value should be
    [('w', 'w'), ('o', ''), ('r', 'r'), ('', o), ('k', 'k')].

    Parameters
    ---
    s1      The source sequences.
    s2      The target sequences.
    counts  A dictionary of dictionaries with counts of edit
            operations (see assignment description for more
            information and an example)
    """
    # INITIALISE EDIT TABLE
    table = np.zeros((len(s1) + 1, len(s2) + 1), dtype=float)
    for i in range(len(table[0])):
        table[0][i] = i  # fill in 1st row with 0, 1, 2...
    for i in range(len(table)):
        table[i][0] = i  # fill in 1st col with 0, 1, 2...

    # FILL IN MINIMUM COST EDIT TABLE
    # (dynamic approach)
    for i in range(1, len(table)):  # skip 1st row
        for j in range(1, len(table[i])):  # skip 1st col
            # map to characters
            ch1 = s1[i - 1]
            ch2 = s2[j - 1]
            # compute costs
            subst = table[i - 1][j - 1] + cost(ch1, ch2, counts)  # substitution or copy
            insert = table[i][j - 1] + cost("", ch1, counts)
            delete = table[i - 1][j] + cost(ch1, "", counts)
            # assign cell value
            table[i][j] = min(subst, insert, delete)

    # FIND EDITS
    edits = []
    i = len(table) - 1
    j = len(table[0]) - 1
    while i != 0 and j != 0:
        # map to characters
        ch1 = s1[i - 1]
        ch2 = s2[j - 1]
        # compute costs
        subst = table[i - 1][j - 1] + cost(ch1, ch2, counts)  # substitution or copy
        insert = table[i][j - 1] + cost("", ch1, counts)
        delete = table[i - 1][j] + cost(ch1, "", counts)

        # find edit
        edit = tuple()
        operation = np.argmin([delete, insert, subst])
        if operation == 0:  # delete
            edit = (ch1, "")
            i -= 1
        elif operation == 1:  # insert
            edit = ("", ch1)
            j -= 1
        elif operation == 2:  # substitution or copy
            edit = (ch1, ch2)
            i -= 1
            j -= 1

        edits.append(edit)

    edits.reverse()
    return edits


def count_edits(filename: str, counts: dict = None) -> dict:
    """ Calculate and return pairs of letters aligned by find_edits().

    Parameters
    ---
    filename    A file containing word - misspelling pairs.
                One pair per line, pairs separated by tab.
    counts      If given use as initial counts.
    """
    # INITIALISE DICT
    # retrieve alphabet
    alphabet = [""]
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            for char in line.strip():
                if char not in alphabet:
                    alphabet.append(char)
    alphabet.remove("\t")
    # build dict structure with 0 counts
    counts_new = dict()
    for ch1 in alphabet:
        counts_new.update({ch1: dict()})
        for ch2 in alphabet:
            counts_new[ch1].update({ch2: 0})

    # COUNT EDITS
    with open(filename, "r", encoding="utf-8") as pairs:
        # find edits for each pair of words
        for pair in pairs:
            s1, s2 = pair.strip().split("\t")
            # count edits
            for edit in find_edits(s1, s2, counts):
                ch1, ch2 = edit
                counts_new[ch1][ch2] = counts_new[ch1][ch2] + 1

    return counts_new


if __name__ == "__main__":
    # The code below shows the intended use of your implementation above.
    import json

    counts = None
    counts_new = count_edits('spelling-data.txt')
    while counts != counts_new:
        counts = counts_new
        counts_new = count_edits('spelling-data.txt', counts)
    with open('spell-errors.json', 'wt') as f:
        json.dump(counts, f, ensure_ascii=False, indent=2)
