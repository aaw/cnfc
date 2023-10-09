from collections import defaultdict
from functools import reduce
from .tseytin import *
from .cardinality import at_most_one_true
import sre_parse
import uuid

# Functions in this module rely on Python's built-in sre_parse library to do the
# initial parsing of a regex string into an abstract syntax tree. We then
# convert that AST to an NFA, and the NFA to a DFA. We don't support everything
# that sre_parse supports and just raise an error if we hit some unsupported
# construct. Some examples of sre_parse output, since I couldn't find any
# other good reference:
#
# >>> sre_parse.parse('01')
# [(LITERAL, 48), (LITERAL, 49)]
# >>> sre_parse.parse('0*')
# [(MAX_REPEAT, (0, MAXREPEAT, [(LITERAL, 48)]))]
# >>> sre_parse.parse('0+')
# [(MAX_REPEAT, (1, MAXREPEAT, [(LITERAL, 48)]))]
# >>> sre_parse.parse('0?')
# [(MAX_REPEAT, (0, 1, [(LITERAL, 48)]))]
# >>> sre_parse.parse('0{1,3}')
# [(MAX_REPEAT, (1, 3, [(LITERAL, 48)]))]
# >>> sre_parse.parse('0?1')
# [(MAX_REPEAT, (0, 1, [(LITERAL, 48)])), (LITERAL, 49)]
# >>> sre_parse.parse('0{1,3}1*')
# [(MAX_REPEAT, (1, 3, [(LITERAL, 48)])), (MAX_REPEAT, (0, MAXREPEAT, [(LITERAL, 49)]))]
# >>> sre_parse.parse('(01){1,3}')
# [(MAX_REPEAT, (1, 3, [(SUBPATTERN, (1, 0, 0, [(LITERAL, 48), (LITERAL, 49)]))]))]
# >>> sre_parse.parse('(01)*').dump()
# MAX_REPEAT 0 MAXREPEAT
#   SUBPATTERN 1 0 0
#     LITERAL 48
#     LITERAL 49
# >>> sre_parse.parse('(1)*').dump()
# MAX_REPEAT 0 MAXREPEAT
#   SUBPATTERN 1 0 0
#      LITERAL 49
# >>> sre_parse.parse('1*').dump()
# MAX_REPEAT 0 MAXREPEAT
#   LITERAL 49
# >>> sre_parse.parse('(00|11)').dump()
#   SUBPATTERN 1 0 0
#     BRANCH
#       LITERAL 48
#       LITERAL 48
#     OR
#       LITERAL 49
#       LITERAL 49

# We only support a binary alphabet of {0,1}. NFAs also need an epsilon for transitions.
ZERO = 48
ONE = 49
EPSILON = -1

class NFA:
    def __init__(self, initial, accepting, delta):
        self.initial = initial
        self.accepting = accepting
        self.delta = delta

    def debug(self):
        print('initial: {}'.format(self.initial[:6]))
        print('accept:  {}'.format([x[:6] for x in self.accepting]))
        for k,v in self.delta.items():
            if v.get(ZERO) is not None: print('d[{}][0] = {}'.format(k[:6], [vv[:6] for vv in v[ZERO]]))
            if v.get(ONE) is not None: print('d[{}][1] = {}'.format(k[:6], [vv[:6] for vv in v[ONE]]))
            if v.get(EPSILON) is not None: print('d[{}][ε] = {}'.format(k[:6], [vv[:6] for vv in v[EPSILON]]))

class DFA:
    def __init__(self, initial, accepting, delta):
        self.initial = initial
        self.accepting = accepting
        self.delta = delta

    def debug(self):
        print('initial: {}'.format(self.initial[:6]))
        print('accept:  {}'.format([x[:6] for x in self.accepting]))
        for k,v in self.delta.items():
            if v.get(ZERO) is not None: print('d[{}][0] = {}'.format(k[:6], v[ZERO][:6]))
            if v.get(ONE) is not None: print('d[{}][1] = {}'.format(k[:6], v[ONE][:6]))

def new_state():
    return uuid.uuid4().hex

# Delta transitions map a state to a map of literal to set of states
def new_nfa_delta():
    return defaultdict(lambda: defaultdict(set))

def regex_to_dfa(s):
    parsed = sre_parse.parse(s)
    return minimize_dfa(nfa_to_dfa(thompson_nfa(parsed)))

def thompson_nfa(expr):
    if type(expr) == sre_parse.SubPattern:
        # parse each expression in the list, concatenate with epsilon transitions
        nfas = [thompson_nfa(subexpr) for subexpr in expr]
        delta = new_nfa_delta()
        for nfa in nfas:
            delta.update(nfa.delta)
        # Connect all accepting states in nfa i-1 to initial states in nfa i via epsilon transitions
        for i in range(1,len(nfas)):
            for state in nfas[i-1].accepting:
                delta[state][EPSILON].add(nfas[i].initial)
        if nfas:
            initial = nfas[0].initial
            accepting = nfas[-1].accepting
        else:  # empty subpattern, accepts only empty string
            state = new_state()
            initial, accepting = state, {state}
        return NFA(initial, accepting, delta)
    elif type(expr) == tuple:
        if expr[0] == sre_parse.LITERAL:
            lit = expr[1]
            if lit not in (ZERO,ONE): raise ValueError("Only binary alphabet {0,1} supported.")
            initial, final = new_state(), new_state()
            delta = new_nfa_delta()
            delta[initial][lit].add(final)
            return NFA(initial, {final}, delta)
        elif expr[0] == sre_parse.IN or expr[0] == sre_parse.BRANCH:
            exprs = expr[1] if expr[0] == sre_parse.IN else expr[1][1]
            nfas = [thompson_nfa(subexpr) for subexpr in exprs]
            delta = new_nfa_delta()
            for nfa in nfas:
                delta.update(nfa.delta)
            # make a new initial state with epsilon transitions to all nfas
            initial = new_state()
            for nfa in nfas:
                delta[initial][EPSILON].add(nfa.initial)
            accepting = reduce(lambda x,y: x | y, (nfa.accepting for nfa in nfas), set())
            return NFA(initial, accepting, delta)
        elif expr[0] == sre_parse.SUBPATTERN:
            # SUBPATTERN appears like:
            # sre_parse.parse('(0)') == (SUBPATTERN, (1, 0, 0, [(LITERAL, 48)]))
            # I don't know what the 1,0,0 represent here but it's probably capture groups,
            # which we don't support. So I'm just ignoring them.
            return thompson_nfa(expr[-1][-1])
        elif expr[0] == sre_parse.MAX_REPEAT:
            # MAX_REPEAT appears like:
            # sre_parse.parse('0?') == (MAX_REPEAT, (0, 1, [(LITERAL, 48)])) or
            # sre_parse.parse('0+') == (MAX_REPEAT, (1, MAXREPEAT, [(LITERAL, 48)]))
            min_repeat, max_repeat = expr[1][0], expr[1][1]
            initial, final = new_state(), new_state()
            delta = new_nfa_delta()
            # We need at least one copy of the underlying NFA. If max_repeat is MAXREPEAT
            # need only one copy. Otherwise, we need max_repeat copies, with epsilon
            # transitions to the final state from all states after the min_repeat copy.
            num_copies = 1 if max_repeat == sre_parse.MAXREPEAT else max_repeat
            copies = [thompson_nfa(expr[1][2]) for i in range(num_copies)]
            for copy in copies:
                delta.update(copy.delta)
            for i in range(1,len(copies)):
                for state in copies[i-1].accepting:
                    delta[state][EPSILON].add(copies[i].initial)
            delta[initial][EPSILON].add(copies[0].initial)
            for state in copies[-1].accepting:
                delta[state][EPSILON].add(final)
            if max_repeat == sre_parse.MAXREPEAT:
                delta[final][EPSILON].add(initial)
            if min_repeat == 0:
                delta[initial][EPSILON].add(final)
            else:  # min_repeat > 0
                for i in range(min_repeat, len(copies)):
                    for state in copies[i-1].accepting:
                        delta[state][EPSILON].add(final)
            return NFA(initial, {final}, delta)
        else:
            raise ValueError("Unsupported regular expression construct: {}".format(expr))
    else:
        raise Exception("Unexpected input: {}".format(expr))

def epsilon_closure(nfa, states):
    image = states
    while True:
        old_image = image
        for state in old_image:
            image = image | nfa.delta[state][EPSILON]
        if len(old_image) == len(image): break
    return image

def set_id(s):
    return '{:x}'.format(reduce(lambda x,y: x ^ y, (int(h, 16) for h in s), 0))

def nfa_to_dfa(nfa):
    # DFA id -> NFA set of states
    delta = defaultdict(dict)
    initial = epsilon_closure(nfa, {nfa.initial})
    accepting = set()
    if initial & nfa.accepting:
        accepting.add(set_id(initial))
    stack = [initial]
    while stack:
        state = stack.pop()
        state_id = set_id(state)
        for transition in (ZERO, ONE):
            trans_state = epsilon_closure(
                nfa, reduce(lambda x,y: x | y, (nfa.delta[s][transition] for s in state), set()))
            trans_state_id = set_id(trans_state)
            if trans_state_id != '0':
                if delta.get(trans_state_id) is None:
                    stack.append(trans_state)
                if trans_state & nfa.accepting:
                    accepting.add(trans_state_id)
                delta[state_id][transition] = trans_state_id

    return DFA(set_id(initial), accepting, delta)

def minimize_dfa(dfa):
    # TODO
    return dfa

# Generate CNF clauses that are true iff the given regex matches the tuple of literals.
def regex_match(formula, tup, regex):
    all_states = set()
    dfa = regex_to_dfa(regex)
    for k,v in dfa.delta.items():
        all_states.add(k)
        if v.get(ONE) is not None: all_states.add(v[ONE])
        if v.get(ZERO) is not None: all_states.add(v[ZERO])

    # zero_trans[s] = {a,b,c} if there's a transition from a,b,c to s on zero
    zero_trans = defaultdict(set)
    # one_trans[s] = {a,b,c} if there's a transition from a,b,c to s on one
    one_trans = defaultdict(set)
    for k,v in dfa.delta.items():
        if v.get(ONE) is not None: one_trans[v[ONE]].add(k)
        if v.get(ZERO) is not None: zero_trans[v[ZERO]].add(k)

    # vs[(state,i)] == dfa is in state at time i
    vs = {}
    for s in all_states:
        for i in range(len(tup)+1):
            vs[(s,i)] = formula.AddVar()

   #  i = 0: Must start in initial state, can't start in any other state.
    for state in all_states:
        if state == dfa.initial:
            yield (vs[(state,0)],)
        else:
            yield (~vs[(state,0)],)

    # For i > 0, set vs[(state,i)] equal to conditions from time i-1 that would
    # make it true: you have to be in a state at time i-1 that could transition
    # to the given state given tup[i-1].
    for i in range(1,len(tup)+1):
        for state in all_states:
            # vs[(s,i)] == (tup[i-1] AND (vs[(s1,i-1)] OR vs[(s2,i-1)] OR ...))
            #              OR
            #              (~tup[i-1] AND (vs[t1,i-1)] OR vs[(t2,i-1)] OR ...))
            # for all states s1, s2, ... with transitions to s on 1 and t1, t2, ...
            # with transitions to s on 0.
            zero_conj, one_conj = None, None
            if zero_trans[state]:
                big_or = formula.AddVar()
                yield from gen_or([vs[(s,i-1)] for s in zero_trans[state]], big_or)
                zero_conj = formula.AddVar()
                yield from gen_and((big_or, ~tup[i-1]), zero_conj)
            if one_trans[state]:
                big_or = formula.AddVar()
                yield from gen_or([vs[(s,i-1)] for s in one_trans[state]], big_or)
                one_conj = formula.AddVar()
                yield from gen_and((big_or, tup[i-1]), one_conj)
            # We can optimize the encoding a little bit because we know the transitions
            # ahead of time and can use them to simplify the big disjunction of conjunctions
            # above.
            if zero_conj is None and one_conj is None:
                yield (~vs[(state,i)],)
            elif zero_conj is None:
                yield (vs[(state,i)], ~one_conj)
                yield (~vs[(state,i)], one_conj)
            elif one_conj is None:
                yield (vs[(state,i)], ~zero_conj)
                yield (~vs[(state,i)], zero_conj)
            else:
                disj = formula.AddVar()
                yield from gen_or((one_conj, zero_conj), disj)
                yield (vs[(state,i)], ~disj)
                yield (~vs[(state,i)], disj)

    # Must end in accepting state.
    yield [vs[(state,len(tup))] for state in dfa.accepting]
