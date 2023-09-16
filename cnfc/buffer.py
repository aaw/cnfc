# A clause buffer
import tempfile

class Buffer:
    def __init__(self):
        fd, path = tempfile.mkstemp()
        self.fd = open(path, 'r+')
        cfd, cpath = tempfile.mkstemp()
        self.cfd = open(cpath, 'r+')
        self.maxvar = 0
        self.num_clauses = 0
        self.checkpoints = []

    def __del__(self):
        self.fd.close()
        self.cfd.close()

    def PushCheckpoint(self):
        self.checkpoints.append((self.num_clauses, self.maxvar, self.fd.tell()))

    def PopCheckpoint(self):
        self.num_clauses, self.maxvar, pos = self.checkpoints.pop()
        self.fd.seek(pos)
        self.fd.truncate()

    def Append(self, clause):
        if len(clause) > 0: self.maxvar = max(self.maxvar, *[abs(lit) for lit in clause])
        self.num_clauses += 1
        self.fd.write("{} 0\n".format(' '.join(str(lit) for lit in clause)))

    def AddComment(self, comment):
        self.cfd.write("c {}\n".format(comment))

    def Flush(self, fd):
        self.cfd.seek(0)
        fd.write(self.cfd.read())
        fd.write('p cnf {} {}\n'.format(self.maxvar, self.num_clauses))
        self.fd.seek(0)
        fd.write(self.fd.read())
