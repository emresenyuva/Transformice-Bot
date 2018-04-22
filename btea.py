#!/usr/bin/env python

def encode(v, n, k):
	DELTA = 0x9e3779b9
	def MX():
        	return ((z>>5)^(y<<2)) + ((y>>3)^(z<<4))^(sum^y) + (k[(p & 3)^e]^z)

	y = v[0]
    	sum = 0
    	if n > 1:
        	z = v[n - 1]
        	q = 6 + 52 / n
		while q > 0:
		    q -= 1
		    sum = (sum + DELTA) & 0xffffffff
		    e =  ((sum >> 2) & 0xffffffff) & 3
		    p = 0
		    while p < n - 1:
		        y = v[p + 1]
		        z = v[p] = (v[p] + MX()) & 0xffffffff
		        p += 1
		    y = v[0]
		    z = v[n - 1] = (v[n - 1] + MX()) & 0xffffffff
	return 0
