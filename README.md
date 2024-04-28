# cnfc

A [CNF](https://en.wikipedia.org/wiki/Conjunctive_normal_form) compiler that generates
compact DIMACS CNF encodings from higher-level primitives in Python. DIMACS CNF is
the input format accepted by most SAT solvers.

In contrast to optimization libraries like Z3, PySAT or ortools that provide both
a language for modeling optimization problems and integrated solvers,
cnfc only generates DIMACS CNF files and expects you to bring your own SAT solver to
solve the output formula. This works better for harder combinatorial problems that
may take hours or days to solve, since it gives you the flexibility to run your own
preprocessing or cubing as an intermediate step or pass the input to one or more
solvers that might work best on your problem.

Read on for an extended example or look at the [examples](examples) in this repository
to get started.

## Example

Suppose you need to schedule 8 employees to cover two shifts a day (7 a.m. - 3 p.m. and
3 p.m. - 11 p.m.) for the whole week. Every shift needs to be staffed
by two employees, one of which has to be a manager. Each employee has a few shifts where
they can't work. You need to give everyone at least 3 shifts of
work for the week but they can't go over 4. Employees can't work both the morning and
night shift on the same day.

This is a collection of constraints that should be easy to solve with a SAT solver, but
encoding them into a propositional formula can be tedious. Here's how to do it with cnfc:

```python
from cnfc import *

employees = ['Homer', 'Hamza', 'Veronica', 'Lottie', 'Zakaria', 'Keeley', 'Farhan', 'Seamus']
managers = ['Homer', 'Hamza', 'Keeley', 'Farhan']
days = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
hours = ['7-3','3-11']
shifts = [f'{day} {hour}' for day in days for hour in hours]

# Associate a boolean variable with each pairing of employee and shift.
formula = Formula()
varz = dict(((employee, shift), formula.AddVar(f'{employee} {shift}'))
            for employee in employees for shift in shifts)

# Every shift needs exactly two people scheduled.
for shift in shifts:
    scheduled = [varz[(employee, shift)] for employee in employees]
    formula.Add(NumTrue(*scheduled) == 2)

# Every shift needs a manager.
for shift in shifts:
    manager_on_shift = [varz[(manager, shift)] for manager in managers]
    formula.Add(Or(*manager_on_shift))

# People have shifts they can't work.
formula.Add(Not(varz[('Homer', 'Sun 7-3')]))
formula.Add(Not(varz[('Lottie', 'Tue 7-3')]))
formula.Add(Not(varz[('Lottie', 'Tue 3-11')]))
formula.Add(Not(varz[('Farhan', 'Fri 3-11')]))
formula.Add(Not(varz[('Homer', 'Sat 3-11')]))
formula.Add(Not(varz[('Hamza', 'Sat 3-11')]))
formula.Add(Not(varz[('Keeley', 'Sat 3-11')]))

# Each employee needs to work at least 3 shifts but no more than 4.
for employee in employees:
    employee_shifts = [varz[(employee,shift)] for shift in shifts]
    formula.Add(NumTrue(*employee_shifts) >= 3)
    formula.Add(NumTrue(*employee_shifts) <= 4)

# People can't work both the morning and night shift in a single day.
for employee in employees:
    for day in days:
        formula.Add(Not(And(varz[(employee, f'{day} 7-3')],
                            varz[(employee, f'{day} 3-11')])))

# This function will be called to print the final schedule once we've solved for
# it. The extra_args will be full descriptions of the shift staffings -- the
# same strings we used to name the variables in our calls to AddVar above.
def print_solution(sol, *extra_args):
    for shift_assignment in extra_args[0]:
        if sol[shift_assignment]:
            print(shift_assignment)

# Write the resulting CNF file to /tmp/cnf.
with open('/tmp/cnf', 'w') as f:
    formula.WriteCNF(f)
# Write an extractor script to /tmp/extractor.py.
with open('/tmp/extractor.py', 'w') as f:
    shift_assignments = [f'{employee} {shift}' for shift in shifts for employee in employees]
    formula.WriteExtractor(f, print_solution, extra_args=[shift_assignments])
```

This script will generate a DIMACS CNF file (/tmp/cnf) and a script (/tmp/extractor.py) that will
let you extract and print out the solution from the solver output. You'll need a SAT solver like
[kissat](https://github.com/arminbiere/kissat) or [cadical](https://github.com/arminbiere/cadical)
to solve the CNF file.

To see the solution, run the script above, then run a solver on the CNF file, saving the output:

```
$ kissat /tmp/cnf > /tmp/solver-output
```

and finally, run the extractor script on the CNF file and the output of the solver:

```
$ python3 /tmp/extractor.py /tmp/cnf /tmp/solver-output
```

You should see a complete schedule like:

```
Zakaria Sun 7-3
Farhan Sun 7-3
Homer Sun 3-11
Seamus Sun 3-11
Hamza Mon 7-3
Seamus Mon 7-3
Zakaria Mon 3-11
Keeley Mon 3-11
Homer Tue 7-3
Zakaria Tue 7-3
Keeley Tue 3-11
Seamus Tue 3-11
Homer Wed 7-3
Seamus Wed 7-3
Lottie Wed 3-11
Keeley Wed 3-11
Veronica Thu 7-3
Farhan Thu 7-3
Lottie Thu 3-11
Keeley Thu 3-11
Hamza Fri 7-3
Farhan Fri 7-3
Homer Fri 3-11
Veronica Fri 3-11
Hamza Sat 7-3
Veronica Sat 7-3
Lottie Sat 3-11
Farhan Sat 3-11
```

You can verify that all of our constraints are satisfied. Right now, three of the four managers (Homer, Hamza, and Keeley)
want the Saturday 3-11 shift off, so if we change the script to add another constraint with the last remaining manager
(Farhan) asking for that shift off:

```
formula.Add(Not(varz[('Farhan', 'Sat 3-11')]))
```

and then re-run the solver and extractor, we should see:

```
UNSATISFIABLE
```

instead of a schedule, which tells us that there's no assignment of people to shifts that satisfies all of the criteria we've laid out.

A [runnable version of this script](examples/scheduling) is in the [examples subdirectory](examples) of this repository.

## Features

Arbitrary clauses can be built, composed, and added to formulas with:

   * Familiar boolean operators `And`, `Or`, `Not`, `If`, `Eq`, `Neq`.
   * `Tuple`s that can be compared for equality, inequality, or lexicographic order.
   * `Integer`s that can be added, multiplied, or compared as `Tuple`s (see [examples/prime](examples/prime)).
   * `NumTrue` and `NumFalse` for cardinality constraints (see [examples/nqueens](examples/nqueens)).
   * `RegexMatch` to apply binary regular expressions to `Tuple`s (see [examples/nonagram](examples/nonagram)).

## Installation

cnfc is tested on [these versions](https://github.com/aaw/cnfc/blob/master/.github/workflows/python-package.yml#L19) of Python 3. To install
the latest stable release of cnfc, run:

```
pip install cnfc
```

## Development

Install [poetry](https://python-poetry.org/docs/#installation) and run `poetry install`. Then you can bring up a shell, etc. Run tests with:

```
poetry run python3 -m unittest discover
```

To release a new version to PyPI, bump the version in `pyproject.toml` and run:

```
poetry publish --build --username=__token__ --password=$PYPI_TOKEN
```