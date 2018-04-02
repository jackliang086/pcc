import sys
sys.path.append("..")
from csymbol import *

if __name__ == '__main__':
    '''
    example code
    int a;
    int main(int a,int b){
       int b;
    }
    '''

    sm = SymbolManager()

    sm.ident_install('a')
    sm.enter_scope()
    sm.ident_install('a')
    sm.ident_install('b')
    sm.enter_scope()
    sm.ident_install('c')

    #sm.exit_scope()
    s = sm.lookup(sm.identifiers, 'b')
    print('lookup {}'.format(s))

    sm.see_all(sm.identifiers)



