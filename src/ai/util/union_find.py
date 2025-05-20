class UnionFind:
    def __init__(self, n: int):
        self.root = [ i for i in range(n) ]

    def find(self, i: int):
        if i != self.root[i]:
            self.root[i] = self.find(self.root[i])
        return self.root[i]
    
    def merge(self, a: int, b: int) -> bool:
        a = self.find(a)
        b = self.find(b)

        if a == b:
            return False
        
        self.root[a] = b
        return True