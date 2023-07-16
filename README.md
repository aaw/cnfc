# cnfc
A Python module that generates DIMACS CNF files

```python
from cnfc import Formula, And, Or, IfThen

f = Formula()
x, y, z = f.AddVars('x,y,z,w')

f.AddClause(-x,y)  # Equivalent to f.AddClause(And(-x,y))
f.AddClause(-y,z)
f.AddClause(-z,x)

f.AddClause(Or(IfThen(x,y), And(z,w)))

f.AddClause(ExactlyNTrue(2, [x,y,z]))

f.Write('/tmp/myfile.cnf')
```