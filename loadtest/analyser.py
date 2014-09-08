import sys
from math import ceil

rcount = 0
scount = 0
qtimes = []

with open(sys.argv[1]) as f:
    for line in f:
        rc, qt = line.split()
        scount += 1
        rcount += int(rc)
        qtimes.append(float(qt))

qtimes.sort()

print '%d results in %d searches (mean %d)' % (rcount, scount, (rcount / scount))
print '%0.2fs mean query time, %0.2fs max, %0.2fs min' % (sum(qtimes) / scount, qtimes[-1], qtimes[0])
print '50%%   of qtimes <= %0.2fs' % qtimes[int(ceil(scount * 0.50))]
print '90%%   of qtimes <= %0.2fs' % qtimes[int(ceil(scount * 0.90))]
print '99%%   of qtimes <= %0.2fs' % qtimes[int(ceil(scount * 0.99))]
print '99.9%% of qtimes <= %0.2fs' % qtimes[int(ceil(scount * 0.999))]


