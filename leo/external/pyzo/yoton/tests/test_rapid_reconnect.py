import yoton

verbosity = 0
def connect_test():
    c1 = yoton.Context(verbosity)
    c2 = yoton.Context(verbosity)
    c3 = yoton.Context(verbosity)

    c1.bind('localhost:test1')
    c2.connect('localhost:test1')

    c2.bind('localhost:test2')
    c3.connect('localhost:test2')

    c1.close()
    c2.close()
    c3.close()

for i in range(5):
    print('iter', i)
    connect_test()
