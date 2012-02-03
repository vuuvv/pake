import os
from pake import pakefile

@task()
def test(depends, target):
	print depends
	cd("src")
	print target
#from pake import cc, task, cd
#
#src = ['hello.c', 'main.c']
#
#hello_obj = cfile('hello.c', ['hello.h'])
#main_obj = cfile('main.c')
#
#@task([hello_obj, main_obj], default=True)
#def main(depends, target):
#	cd("src")
#	cc.link(target, depends)
