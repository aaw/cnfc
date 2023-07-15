# cnfc
A Python module that generates DIMACS CNF files

```python
from cnfc import Formula

f = Formula()
x, y, z = f.AddVars('x,y,z')
f.AddClause(-x,y)
f.AddClause(-y,z)
f.AddClause(-z,x)

f.Write('/tmp/myfile.cnf')
```