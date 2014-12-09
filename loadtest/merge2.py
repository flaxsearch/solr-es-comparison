import sys

def get_qtimes_sorted(fname):
    qtimes = []
    with open(fname) as f:
        for line in f:
            rc, qt = line.split()
            qtimes.append(float(qt))
    qtimes.sort()
    return qtimes

qtimes1 = get_qtimes_sorted(sys.argv[1])
qtimes2 = get_qtimes_sorted(sys.argv[2])
assert len(qtimes1) == len(qtimes2)

with open(sys.argv[3], 'w') as f:
    print >>f, sys.argv[4]
    for n, (q1, q2) in enumerate(zip(qtimes1, qtimes2)):
        print >>f, '{0}, {1}, {2}'.format(n, q1, q2)
