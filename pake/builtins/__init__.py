"""
package for buildin tasks
"""

from pake.core import task, option
from pake.globals import app
cd = app.cd

@task()
def ls(depends):
	print 'ls'
