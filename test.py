#!/usr/bin/env python
"""
Test PLI Application
Copyright (C) 2012 Ace Internet Services Pty Ltd

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import pli
import time

p = pli.PLI(('172.31.2.90', 26000), timeout=30, retries=5, retry_delay=5.0)
#p = pli.PLI('/dev/null')

assert p.loopback_test() # check everything is A-OK

print 'battery voltage is %d' % p.get_value(pli.BATTERY_VOLTAGE)
print 'battery temp is %d' % p.get_value(pli.BATTERY_TEMP)
