#!/usr/bin/env python

import pli
import time

p = pli.PLI(('172.31.2.110', 26000))
#p = pli.PLI('/dev/null')

assert p.loopback_test() # check everything is A-OK

for i in range(0x00,0x100):
	t1 = time.time()
	v = p.get_value(i)
	t2 = time.time()
	tdelta = t2 - t1
	print '%x = %d    \t(took %f seconds)' % (i, v, tdelta)
	time.sleep(0.1)
