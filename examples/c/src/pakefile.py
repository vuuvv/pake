import os
from pake import pakefile

@task(default=True)
def test(depends, target):
	print "test"
#from pake import cc, task
#
#src = ['hello.c']
#
#hello_obj = cfile('hello.c', ['hello.h'], default=True)

