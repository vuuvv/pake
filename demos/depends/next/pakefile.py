
print dir()

@task(['d1'])
def next(t):
	print t.target
