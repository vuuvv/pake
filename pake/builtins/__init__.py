"""
package for buildin tasks
"""

from pake.core import task, option
from pake.context import app
cd = app.cd

@task()
def ls(depends, target):
	print 'ls'
