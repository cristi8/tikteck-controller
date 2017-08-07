#!/usr/bin/env python

import tikteck2
import sys
import random
import time

a = []
for i in range(4):
    a.append(int(sys.argv[i+1]))

# TODO: Change bulb mac address and name/password. See https://github.com/mjg59/python-tikteck for details
bulb = tikteck2.tikteck("00:21:4D:00:00:00", "Smart Light", "234")
bulb.connect()

bulb.set_state(a[0], a[1], a[2], a[3])
