
print dir()

@task(['d1'])
def next(depends, target):
	print target
