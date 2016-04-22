# Test file for python-3 related parsing.

# See http://joao.npimentel.net/2015/07/23/python-2-vs-python-3-ast-differences/

# Keywords, etc, in base-class...

class Foo1(metaclass=MyMetaClass):
    pass
    
    
class Foo2(base1, base2, metaclass=mymeta):
    pass

class Foo(*bases, **kwds):
    pass
    
# Function args & annotions...

def fn(a: "first argument", b: int, *, c=2) -> "result":
    pass
    
# With statement.
# 2: generates two With nodes.
# 3: generates one With node and two withitem nodes.

with open('a', 'w') as f1, open('b', 'w') as f2:
    pass

# nonlocal...

def outer():
    a = 1
    def inner():
        nonlocal a
        a += 2
    inner()
    
# yield from...

def my_generator():
    yield from other_generator()