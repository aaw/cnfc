from collections import defaultdict
from functools import reduce
import sre_parse
import uuid

# sre_parse.parse(r'0*1+').dump()

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

ZERO = 48
ONE = 49
EPSILON = -1

class NFA:
    def __init__(self, initial, accepting, delta):
        self.initial = initial
        self.accepting = accepting
        self.delta = delta

class DFA:
    def __init__(self, initial, accepting, delta):
        self.initial = initial
        self.accepting = accepting
        self.delta = delta

    def accepts(self, s):
        state = self.initial
        m = {'0': ZERO, '1': ONE}
        for ch in s:
            xch = m.get(ch)
            if xch is None: return False
            state = self.delta[state].get(xch)
            if state is None: return False
        return state == self.accepting

def new_state():
    return uuid.uuid4().hex

# Delta transitions map a state to a map of literal to set of states
def new_nfa_delta():
    return defaultdict(lambda: defaultdict(set))

def regex_to_dfa(s):
    parsed = sre_parse.parse(s)
    return nfa_to_dfa(thompson_nfa(parsed))

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

    return DFA(set_id(initial), set_id(accepting), delta)
