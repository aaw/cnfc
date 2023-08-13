# cnfc
A Python module that generates DIMACS CNF files

```python
from cnfc import *

f = Formula()
x, y, z, w = f.AddVars('x,y,z,w')

f.AddClause(~x,y)  # Equivalent to f.Add(Or(~x,y))
f.AddClause(~y,z)
f.AddClause(~z,x)

# Same as f.Add(Or(Implies(x,y),Not(And(z,w))))
f.Add(Implies(x,y) | ~(z & w))

f.Add(NumTrue(x,y,z) >= 1)

f.Add(Tuple(x,y) < Tuple(z,w))

with fd as open('/tmp/output.cnf', 'w'):
    f.WriteCNF(fd)
```

Running tests
=============

```
poetry run python3 -m unittest discover
```