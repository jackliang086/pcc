'''
Copyright 2018 JackLiang.

Hash Map
'''

class HashMap(object):

    def __init__(self, size):
        self.table = [] * size
        for i in range(size):
            self.table.append([])

    def hash(self, k):
        return abs(hash(k)) % len(self.table)

    def __getitem__(self, index):
        return self.table[index]

    def __len__(self):
        return len(self.table)
