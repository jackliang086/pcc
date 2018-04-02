import sys
sys.path.append("..")

class Abc(object):

    def next(self, c):
        print(c)

bbb = 'b'
def check_if(index):
    print('check_if ' + str(index))
    return bbb

if __name__ == '__main__':
    a = 'b'
    if not a == 'c':
        print('aaaaa')
    else:
        print('bbbbb')

    print('Y' if False else 'X')

    a = Abc()
    a.next('ddd')
    print(float('.1'))

    table = [[]] * 256
    print(len(table[1]))
