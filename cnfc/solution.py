class Solution:
    def __init__(self, sol):
        self.sol = sol

    def __getitem__(self, key):
        return self.sol[key]

    def integer(self, *args):
        if len(args) == 1 and isinstance(args[0], str) and args[0] + ':0' in self.sol:
            name = args[0]
            bits = []
            i = 0
            while '{}:{}'.format(name, i) in self.sol:
                bits.append(self.sol['{}:{}'.format(name, i)])
                i += 1
        elif len(args) == 2 and isinstance(args[0], str) and isinstance(args[1], int):
            var, num_bits = args
            bits = [self.sol['{}:{}'.format(var,i)] for i in range(num_bits)]
        elif all(isinstance(arg, str) for arg in args):
            bits = [self.sol[arg] for arg in args]
        else:
            raise TypeError("integer should receive either a string template and num_bits or a sequence of strings")
        # Convert bits to an integer
        result = 0
        for b in bits:
            result *= 2
            result += 1 if b else 0
        if bits and bits[0]:
            result -= 1 << len(bits)
        return result
