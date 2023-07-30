# cnfc
A Python module that generates DIMACS CNF files

```python
from cnfc import Formula, And, Or, IfThen

f = Formula()
x, y, z, w = f.AddVars('x,y,z,w')

f.AddClause(-x,y)  # Equivalent to f.AddClause(And(-x,y))
f.AddClause(-y,z)
f.AddClause(-z,x)

# Same as f.AddClause(Or(Implies(x,y),And(z,w)))
f.AddClause(Implies(x,y) | (z & w))

f.AddClause(NumTrue(x,y,z) >= 1)

f.AddClause(Tuple(x,y) < Tuple(z,w))

f.Write('/tmp/myfile.cnf')
```