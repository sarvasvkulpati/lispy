



Symbol = str              # A Scheme Symbol is implemented as a Python str
Number = (int, float)     # A Scheme Number is implemented as a Python int or float
Atom   = (Symbol, Number) # A Scheme Atom is a Symbol or Number
List   = list             # A Scheme List is implemented as a Python list
Exp    = (Atom, List)     # A Scheme expression is an Atom or List
Env    = dict             # A Scheme environment (defined below) 
                          # is a mapping of {variable: value}



def tokenize(chars: str) -> list:
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()



program = "(begin (define r 10) (* pi (* r r)))"


def read_from_tokens(tokens: list) -> Exp:
  
    if len(tokens) == 0:
        raise SyntaxError('unexpected EOF')

    token = tokens.pop(0)

    if token == '(':
        L = []
        while tokens[0] != ')':
            L.append(read_from_tokens(tokens))
        tokens.pop(0)
        return L
    elif token == ')':
        raise SyntaxError('unexpected )')
    else:
        return atom(token)



def atom(token: str) -> Atom:
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)


def parse(program: str) -> Exp:
    return read_from_tokens(tokenize(program))



import math
import operator as op

def standard_env() -> Env:
    env = Env()
    env.update(vars(math))
    env.update({
        '+': op.add, '-': op.sub, '*': op.mul, '/':op.truediv, '>':op.gt, '<':op.lt, '>=':op.ge, '<=':op.le, '=':op.eq,
        'abs': abs,
        'append': op.add, 
        'apply': lambda proc, args: proc(*args),
        'begin': lambda *x: x[-1],
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:], 
        'cons':    lambda x,y: [x] + y,
        'eq?':     op.is_, 
        'expt':    pow,
        'equal?':  op.eq, 
        'length':  len, 
        'list':    lambda *x: List(x), 
        'list?':   lambda x: isinstance(x, List), 
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [], 
        'number?': lambda x: isinstance(x, Number),  
		'print':   print,
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),

    })
    return env

class Env(dict):
    def __init__(self, params=(), args=(), outer=None):
        self.update(zip(params, args))
        self.outer = outer
    def find(self, var):
        return self if (var in self) else self.outer.find(var)

class Procedure(object):
    def __init__(self, params, body, env):
        self.params, self.body, self.env = params, body, env
    def __call__(self, *args):
        return eval(self.body, Env(self.params, args, self.env))

global_env = standard_env()




def eval(x: Exp, env=global_env) -> Exp:
    if isinstance(x, Symbol):
        return env.find(x)[x]
    elif not isinstance(x, List):
        return x

    op, *args = x

    if op == 'quote':
        return args[0]
    
    elif op == 'if':
        (test, conseq, alt) = args
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env)

    elif op == 'define':
        (symbol, exp) = args
        env[symbol] = eval(exp, env)
    
    elif op == 'set!':
        (symbol, exp) = args
        env.find(symbol)[symbol] = eval(exp, env)
    
    elif op == 'lambda':
        (params, body) =  args
        return Procedure(params, body, env)
    else:
        proc = eval(op, env)
        vals = [eval(arg, env) for arg in args]
        return proc(*vals)

    
def repl(prompt='lis.py> '):
    while True:
        val = eval(parse(input(prompt)))
        if val is not None:
            print(schemestr(val))


def schemestr(exp):
    if isinstance(exp, List):
        print(exp)
        return '(' + ' '.join(map(schemestr, exp)) + ')'
    else:
        return str(exp)

repl()