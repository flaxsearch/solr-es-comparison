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
qtimes3 = get_qtimes_sorted(sys.argv[3])
assert len(qtimes1) == len(qtimes2) == len(qtimes3)

with open(sys.argv[4], 'w') as f:
    print >>f, sys.argv[5]
    for n, (q1, q2, q3) in enumerate(zip(qtimes1, qtimes2, qtimes3)):
        print >>f, '{0}, {1}, {2}, {3}'.format(n, q1, q2, q3)
