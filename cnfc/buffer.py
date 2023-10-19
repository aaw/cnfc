# A clause buffer
import os
import tempfile

class Buffer:
    def __init__(self, visitors=None):
        # We keep two file descriptors:
        #    * fd, which is where we write the raw clauses in DIMACS CNF format,
        #      one by one
        #    * cfd, where we write all comments.
        self.fd, self.cfd = None, None
        fd, self.fpath = tempfile.mkstemp()
        self.fd = open(self.fpath, 'r+')
        cfd, self.cpath = tempfile.mkstemp()
        self.cfd = open(self.cpath, 'r+')
        self.maxvar = 0
        self.num_clauses = 0
        self.checkpoints = []
        self.visitors = [] if visitors is None else visitors

    def __del__(self):
        if self.fd is not None:
            self.fd.close()
            os.remove(self.fpath)
        if self.cfd is not None:
            self.cfd.close()
            os.remove(self.cpath)

    def PushCheckpoint(self):
        self.checkpoints.append((self.num_clauses, self.maxvar, self.fd.tell()))

    def PopCheckpoint(self):
        self.num_clauses, self.maxvar, pos = self.checkpoints.pop()
        self.fd.seek(pos)
        self.fd.truncate()

    def Append(self, clause):
        for visitor in self.visitors:
            visitor.Visit(clause)
        if len(clause) > 0: self.maxvar = max(self.maxvar, *[abs(lit) for lit in clause])
        self.num_clauses += 1
        self.fd.write("{} 0\n".format(' '.join(str(lit) for lit in clause)))

    def AllClauses(self):
        self.fd.seek(0)
        for line in self.fd:
            yield tuple(int(lit) for lit in line.split()[:-1])

    def AddComment(self, comment):
        self.cfd.write("c {}\n".format(comment))

    def AllComments(self):
        self.cfd.seek(0)
        for comment in self.cfd:
            yield comment[2:-1]

    def Flush(self, fd):
        self.cfd.seek(0)
        fd.write(self.cfd.read())
        fd.write('p cnf {} {}\n'.format(self.maxvar, self.num_clauses))
        self.fd.seek(0)
        fd.write(self.fd.read())

# A Buffer visitor that keeps track of unit clauses
class UnitClauses:
    def __init__(self):
        self.units = set()

    def Visit(self, clause):
        if len(clause) != 1: return
        self.units.add(clause[0])
