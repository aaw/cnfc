# Buffers to store clauses during formula creation and simplification.
import os
import tempfile

class MemoryBuffer:
    def __init__(self, maxvar=None):
        self.comments = []
        self.clauses = []
        self.maxvar = 0 if maxvar is None else maxvar
        self.checkpoints = []

    def PushCheckpoint(self):
        self.checkpoints.append((len(self.clauses), len(self.comments), self.maxvar))

    def PopCheckpoint(self):
        num_clauses, num_comments, self.maxvar = self.checkpoints.pop()
        self.clauses = self.clauses[:num_clauses]
        self.comments = self.comments[:num_comments]

    def Append(self, clause):
        if len(clause) > 0: self.maxvar = max(self.maxvar, *[abs(lit) for lit in clause])
        self.clauses.append(clause)

    def AllClauses(self):
        yield from self.clauses

    def AddComment(self, comment):
        self.comments.append(comment)

    def AllComments(self):
        yield from self.comments

    def Flush(self, fd):
        for comment in self.AllComments():
            fd.write("c {}\n".format(comment))
        fd.write('p cnf {} {}\n'.format(self.maxvar, len(self.clauses)))
        for clause in self.AllClauses():
            fd.write("{} 0\n".format(' '.join(str(lit) for lit in clause)))

class FileBuffer:
    def __init__(self, maxvar=None):
        # We keep two file descriptors:
        #    * fd, which is where we write the raw clauses in DIMACS CNF format,
        #      one by one
        #    * cfd, where we write all comments.
        self.fd, self.cfd = None, None
        fd, self.fpath = tempfile.mkstemp()
        self.fd = open(self.fpath, 'r+')
        cfd, self.cpath = tempfile.mkstemp()
        self.cfd = open(self.cpath, 'r+')
        self.maxvar = 0 if maxvar is None else maxvar
        self.num_clauses = 0
        self.checkpoints = []

    def __del__(self):
        if self.fd is not None:
            self.fd.close()
            os.remove(self.fpath)
        if self.cfd is not None:
            self.cfd.close()
            os.remove(self.cpath)

    def PushCheckpoint(self):
        self.checkpoints.append((self.num_clauses, self.maxvar, self.fd.tell(), self.cfd.tell()))

    def PopCheckpoint(self):
        self.num_clauses, self.maxvar, fpos, cfpos = self.checkpoints.pop()
        self.fd.seek(fpos)
        self.fd.truncate()
        self.cfd.seek(cfpos)
        self.cfd.truncate()

    def Append(self, clause):
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
