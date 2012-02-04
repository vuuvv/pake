import os

@task()
def d1(depends, target):
	print target,

@task(['d1'])
def d2(depends, target):
	print target,

@task(['d1'])
def d3(depends, target):
	print target,

@task(['d3', 'd2', 'd3'])
def test(depends, target):
	print target,

@task()
def test_next(depends, target):
	cd('next', 'next')
