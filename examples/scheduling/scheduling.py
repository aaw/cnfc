from cnfc import *

employees = ['Homer', 'Hamza', 'Veronica', 'Lottie', 'Zakaria', 'Keeley',
             'Farhan', 'Seamus']
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
    shift_assignments = \
        [f'{employee} {shift}' for shift in shifts for employee in employees]
    formula.WriteExtractor(f, print_solution, extra_args=[shift_assignments])
