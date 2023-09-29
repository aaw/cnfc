import inspect
import re

def get_variable_mapping_from_cnf_file(f):
    mapping = {}
    p = re.compile(r'c var (\d+) : (.*)')
    for line in f:
        match = re.match(p, line)
        # We add all of our comments in bulk at the beginning so we can exit
        # early if we don't match.
        if match is None: return mapping
        vid, name = match.groups()
        mapping[name] = int(vid)
    return mapping

def get_vars_set_in_solution(f):
    pos = []
    for line in f:
        if line.startswith('s UNSATISFIABLE'): return None
        if not line.startswith('v'): continue
        pos += [int(x) for x in line[1:].strip().split(' ') if int(x) > 0]
    return set(pos)

def generate_extractor(fd, extractor_fn, extra_fns=None, extra_args=None):
    if extra_args is None:
        extra_args = []
    imports = ['argparse', 're', 'sys']
    for line in imports: fd.write(f'import {line}\n')
    fd.write('\n')

    fd.write(inspect.getsource(get_variable_mapping_from_cnf_file))
    fd.write('\n')

    fd.write(inspect.getsource(get_vars_set_in_solution))
    fd.write('\n')

    if extra_fns is not None:
        for fn in extra_fns:
            fd.write(inspect.getsource(fn))
            fd.write('\n')
    fd.write(inspect.getsource(extractor_fn))
    fd.write('\n')

    main = [
        "if __name__ == '__main__':",
        "  parser = argparse.ArgumentParser(description='Solution extractor')",
        "  parser.add_argument('cnf_file', type=str, help='Path to DIMACS CNF file.')",
        "  parser.add_argument('solution_file', type=str, help='Path to output of SAT solver.')",
        "  args = parser.parse_args()",
        "",
        "  with open(args.solution_file) as f: ",
        "    solution = get_vars_set_in_solution(f)",
        "  if not solution:",
        "    print('UNSATISFIABLE')",
        "    sys.exit(1)",
        "  with open(args.cnf_file) as f: ",
        "    mapping = get_variable_mapping_from_cnf_file(f)",
        "  sol = dict((name, id in solution) for name,id in mapping.items())",
        "  {}(sol, *{})".format(extractor_fn.__name__, extra_args),
    ]
    for line in main: fd.write(f'{line}\n')
