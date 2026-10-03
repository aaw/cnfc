import inspect

def write_blocked_cnf(cnf, solution, output, variables):
    assignment = {}
    has_model = False
    for line in solution:
        if line.startswith('s '):
            if line.strip() != 's SATISFIABLE':
                raise ValueError('Expected a satisfiable solver result')
            has_model = True
        elif line.startswith('v'):
            has_model = True
            for literal in line[1:].split():
                literal = int(literal)
                if literal:
                    assignment[abs(literal)] = literal > 0
    if not has_model or any(v not in assignment for v in variables):
        raise ValueError('Solver result must assign every selected variable')
    clause = [-v if assignment[v] else v for v in variables]
    for line in cnf:
        if line.startswith('p '):
            _, kind, num_vars, num_clauses = line.split()
            line = 'p {} {} {}\n'.format(kind, num_vars, int(num_clauses) + 1)
        output.write(line.rstrip('\r\n') + '\n')
    output.write('{} 0\n'.format(' '.join(str(v) for v in clause)))

def generate_blocker(fd, variables):
    fd.write('import argparse\nimport sys\n\n')
    fd.write(inspect.getsource(write_blocked_cnf))
    fd.write('\n')
    main = [
        "if __name__ == '__main__':",
        "  parser = argparse.ArgumentParser(description='Block a solution and write the updated CNF to stdout')",
        "  parser.add_argument('cnf_file', help='Path to DIMACS CNF file.')",
        "  parser.add_argument('solution_file', help='Path to output of SAT solver.')",
        "  args = parser.parse_args()",
        "  try:",
        "    with open(args.cnf_file) as cnf, open(args.solution_file) as solution:",
        "      write_blocked_cnf(cnf, solution, sys.stdout, {})".format(variables),
        "  except ValueError as error:",
        "    parser.error(str(error))",
    ]
    for line in main: fd.write(f'{line}\n')

