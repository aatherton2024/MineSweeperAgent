import cnf
from cnf import Clause, Literal, Cnf
from util import SearchSpace, dfs
from random import shuffle
from search import SatisfiabilitySearchSpace
from collections import defaultdict

def unit_resolve(unit_clauses, clause):
    """Resolves a clause with a set of unit clauses.

    This function resolves the provided clause simultaneously with all
    of the provided unit clauses as follows:
    - If the clause contains the same literal as one of the unit clauses,
      e.g. the clause is !A || !B || C and one the unit clauses is !B, then
      the clause is redundant (entailed by that unit clause) and therefore
      unnecessary. Hence None should be returned.
    - Otherwise, any clause literals whose negations appear in a unit clause
      should be removed, e.g. if the clause is !A || !B || C || !D and the unit
      clauses contain both A and !C, then the resolved clause should be !B || D.

    Parameters
    ----------
    unit_clauses : set[Clause]
        The set of unit clauses.
    clause : Clause
        The clause to resolve with the unit clauses.

    See the examples in test.TestUnitResolve to gain further insight into
    the expected behavior of this function.

    Returns
    -------
    Clause
        The resolved clause (or None if the original clause is redundant)
    """
    # check for redundancy
    clause_literals = clause.get_literals()
    for uc in unit_clauses:
        lit = uc.get_literals()[0]
        if lit in clause_literals: 
            return None
    
    # resolve each unit clause
    new_literals = []
    for literal in clause_literals:
        add = True
        for uc in unit_clauses:
            lit = uc.get_literals()[0]
            if lit.negate() == literal:
                add = False
        if add: new_literals.append(literal)
    
    return Clause(new_literals)



def unit_resolution(unit_clauses, regular_clauses):
    """Resolves a set of clauses with a set of unit clauses.

    This function resolves each regular clause AND unit clause with each unit clause,
    using the unit_resolve function.

    Attention: resolution can produce new unit clauses, and these unit clauses
    must also be resolved with all the other clauses. The process should continue
    until no new clauses can be created through unit resolution.

    See the examples in test.TestUnitResolution to gain further insight into
    the expected behavior of this function.

    Parameters
    ----------
    unit_clauses : set[Clause] -- apparently these are being passed as a list???
        The set of unit clauses.
    regular_clauses : set[Clause]
        The set of non-unit clauses.

    Returns
    -------
    set[Clause], set[Clause]
        The resolved unit clauses and non-unit clauses, respectively.
    """
    unit_clauses = set(unit_clauses)
    regular_clauses = set(regular_clauses)
    iter = True
    while iter:  # while there are still changes in the unit clauses
        newRC = set()
        newUC = False
        for clause in regular_clauses:  # resolve each clause with each unit clause
            new_clause = unit_resolve(unit_clauses, clause)
            if new_clause is None: continue
            elif len(new_clause.get_literals()) == 1: 
                newUC = True
                unit_clauses.add(new_clause)
            else: newRC.add(new_clause)
        
        regular_clauses = newRC
        iter = newUC

    return set(unit_clauses), regular_clauses

class DpllSearchSpace(SatisfiabilitySearchSpace):
    """A search space for the DPLL algorithm."""

    def __init__(self, sent):
        """
        Parameters
        ----------
        sent : Cnf
            a CNF sentence for which we want to find a satisfying model

        """

        super().__init__(sent)
        unit_clauses = set()
        regular_clauses = set()
        for clause in sent.clauses:
            if len(clause) == 1:
                unit_clauses.add(clause)
            else:
                regular_clauses.add(clause)
        self.unit_clauses, self.regular_clauses = unit_resolution(unit_clauses, regular_clauses)

    def get_successors(self, state):
        """Computes the successors of a DPLL search state.

        A search state is a tuple of literals, one for each symbol in the signature.
        As with the SatisfiabilitySearchSpace, the successors of state
        (l_1, ..., l_k) should typically be (l_1, ..., l_k, !s_{k+1}) and
        (l_1, ..., l_k, s_{k+1}), where s_{k+1} is the (k+1)th symbol in the
        signature (according to an alphabetical ordering of the signature symbols).

        However:
        - if self.sent conjoined with literals l_1, ..., l_k entails False (according
          to unit resolution), then there should be no successors, i.e. this method
          should return an empty list
        - if self.sent conjoined with literals l_1, ..., l_k entails !s_{k+1}
          (according to unit resolution), then the only successor should be
          (l_1, ..., l_k, !s_{k+1})
        - if self.sent conjoined with literals l_1, ..., l_k entails s_{k+1},
          (according to unit resolution), then the only successor should be
          (l_1, ..., l_k, s_{k+1}).

        See the examples in test.TestDpllSearchSpace to gain further insight into
        the expected behavior of this method.

        Tips:
        - You can get the "False" clause using the expression cnf.c("FALSE")
        - When you generate both successors (i.e. for both !s_{k+1} and s_{k+1}),
          put the !s_{k+1} successor first in the returned list.

        Parameters
        ----------
        state : tuple[Literal]
            The literals currently assigned by the search node

        Returns
        -------
        list[tuple[Literal]]
            The successor states.
        """

        unit_clauses, regular_clauses = unit_resolution(self.unit_clauses | set([Clause([literal]) for literal in state]), self.regular_clauses)

        ret = []
        if (cnf.c("FALSE")) in regular_clauses: return ret
        
        succ = self.signature[len(state)]
        next = None 

        for clause in unit_clauses:
            if succ == clause.get_literals()[0].get_symbol():
                next = clause.get_literals()[0]
                break
        if next is not None: ret.append(state + tuple([next]))
        else:
            ret.append(state + tuple([Literal(succ, False)]))
            ret.append(state + tuple([Literal(succ)]))
        return ret


def dpll(sent):
    """An implementation of the DPLL algorithm for satisfiability.

    This function will only work once DpllSearchSpace is correctly implemented.

    Parameters
    ----------
    sent : cnf.Sentence
        the CNF sentence for which we want to find a satisfying model.

    Returns
    -------
    dict[str, bool]
        a satisfying model (if one exists), otherwise None is returned
    """

    search_space = DpllSearchSpace(sent)
    state, _ = dfs(search_space)
    model = {lit.get_symbol(): lit.get_polarity() for lit in state} if state is not None else None
    return model

