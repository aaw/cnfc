# A clause buffer
import tempfile

class Buffer:
    def __init__(self):
        fd, path = tempfile.mkstemp()
        self.fd = open(path, 'r+')
        self.maxvar = 0
        self.num_clauses = 0

    def __del__(self):
        self.fd.close()

    def Append(self, clause):
        self.maxvar = max(self.maxvar, *[abs(lit) for lit in clause])
        self.num_clauses += 1
        self.fd.write("{} 0\n".format(' '.join(str(lit) for lit in clause)))

    def Flush(self, fd):
        fd.write('p cnf {} {}\n'.format(self.maxvar, self.num_clauses))
        self.fd.seek(0)
        fd.write(self.fd.read())