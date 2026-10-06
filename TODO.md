# TODO

## RegexMatch over larger alphabets

**Motivation.** `RegexMatch` only accepts strings over `{0,1}`. Supporting
letters and digits would make regex crosswords solvable: each row, column, or
diagonal of letter cells must match its regex. They're a natural fit for SAT
and impossible to express today.

**API.** Extend `RegexMatch` to accept a sequence of cells plus an alphabet,
e.g. `RegexMatch(cells, regex, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ')`, where
each cell is an integer expression whose value indexes into `alphabet`. The
current binary form keeps working unchanged.

**Encoding.** The NFA/DFA construction in `cnfc/regex.py` is already generic
apart from the hardcoded `ZERO`/`ONE` transitions. Generalize transitions to
alphabet symbols, and have each DFA step condition on `cell == index` instead
of a single bit. Those comparisons are cheap and cached since the
literal-to-constant comparison commit. Constructs needed beyond what's
supported today (literals, alternation, `[...]` literal sets, repetition):

- `.` (sre_parse `ANY`)
- negated classes `[^ABC]` and ranges `[A-F]`

**Example.** A regex crossword from Puzzling Stack Exchange or
regexcrossword.com that uses only regular constructs.

**Open questions.**
- Backreferences (`(.)\1`) aren't regular, so they don't fit the DFA approach.
  Many harder regex crosswords (e.g. the well-known MIT hexagonal one) use
  them. Supporting them would need a different encoding, e.g. guessing each
  group's span with position variables and constraining the referenced cells
  to be equal. Decide whether that's v1 or a follow-up; pick the example
  accordingly.
- Should cells also be allowed as one-hot dicts of letter → bool, since some
  puzzles are naturally modeled that way? Integers are probably enough.
