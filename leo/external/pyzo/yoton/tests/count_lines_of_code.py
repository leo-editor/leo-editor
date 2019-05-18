import os

def count_lines(filename):
    
    # Get text
    text = open(filename, 'r').read()
    
    # Init counts: code, docstring, comments, whitespace
    count1, count2, count3, count4 = 0, 0, 0, 0
    
    inDocstring = False
    for line in text.splitlines():
        line = line.strip()
        if '"'*3 in line:
            inDocstring = not inDocstring
        if not line:
            count4 += 1
        elif inDocstring:
            count2 += 1
        elif line.startswith('#') or line.startswith('%'):
            count3 += 1
        else:
            count1 += 1
    
    # Done
    return count1, count2, count3, count4


if __name__ == '__main__':
    
    # Get path of yoton
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.split(path)[0]
    
    # Init files
    files = []
    # Get files in root
    for fname in os.listdir(path):
        files.append(fname)
    # Get files in channels
    for fname in os.listdir(os.path.join(path,'channels')):
        fname = os.path.join('channels', fname)
        files.append(fname)
    
    N1, N2, N3, N4 = 0, 0, 0, 0
    for fname in files:
        if not fname.endswith('.py'):
            continue
        n1, n2, n3, n4 = count_lines(os.path.join(path, fname))
        N1 += n1
        N2 += n2
        N3 += n3
        N4 += n4
        print('%i lines in %s' % (n1, fname))
    
    print('yoton has %i lines in its source' % (N1+N2+N3+N4))
    print('yoton has %i lines of code' % N1)
    print('yoton has %i lines of docstring' % N2)
    print('yoton has %i comment lines' % N3)
    print('yoton has %i lines of whitespace' % N4)
