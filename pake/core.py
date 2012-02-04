"""
Python Makefile System
"""

import os
import sys
import argparse

from imp import new_module
from functools import wraps, partial
from gettext import gettext as _

import pake

class Task(object):
	"""
	A decorator make a function be a sub-command of pake.
	A task function should have 2 argument 'depends' and 'target' at least.
	"""
	def __init__(self, depends=[], target=None, default=False, help=None):
		self.target = target
		self.depends = depends
		self.default = default
		self.help = help
		self.options = []

	def __call__(self, func):
		subparser = pake.app.subparser
		if isinstance(func, Option):
			self.options = func.options
			func = func.func

		if self.target is None:
			self.target = func.__name__

		if self.help is None:
			self.help = self.target
		self.parser = subparser.add_parser(self.target, help=self.help)
		for args, kwargs in self.options:
			self.parser.add_argument(*args, **kwargs)

		helper = partial(func, self.depends, self.target)
		self.func = wraps(func)(helper)
		pake.pakefile.add_task(self)
		return self

def task(*args, **kwargs):
	return Task(*args, **kwargs)

class Option(object):
	def __init__(self, *args, **kwargs):
		self.args = (args, kwargs)

	def __call__(self, func):
		if isinstance(func, Option):
			func.options.append(self.args)
			func = func.func
		else:
			func.options = [self.args]

		self.options = func.options
		self.func = func
		return self

def option(*args, **kwargs):
	return Option(*args, **kwargs)

class PakefileNode(object):
	def __init__(self, path, parent=None):
		self.__children = []
		self.__tasks = {}
		self.module = new_module('pakefile')
		self.default = None
		self.path = os.path.abspath(path)
		if parent is not None:
			parent.add_child(self)
		else:
			self.parent = parent

	def __getattr__(self, name):
		return getattr(self.module, name)

	def add_child(self, node):
		node.parent = self
		self.__children.append(node)

	def add_task(self, t):
		target = t.target
		self.__tasks[target] = t
		if t.default:
			self.default = target

	def find_task(self, target):
		node = self
		while node is not None:
			t = node.__tasks.get(target, None)
			if t is not None:
				return t
			node = node.parent
		raise pake.PakeError("Can't find target '%s'" % target)

	def _run_depend(self, target, completed):
		t = self.find_task(target)
		for d in t.depends:
			if d not in completed:
				completed |= self._run_depend(d, completed)
		t.func()
		completed.add(target)
		return completed

	def run_task(self, target, argv):
		t = self.find_task(target)
		func = t.func
		complete = set()
		for d in t.depends:
			if d not in complete:
				complete |= self._run_depend(d, complete)
		args, argv = t.parser.parse_known_args(argv)
		kwargs = args.__dict__
		func(**kwargs)

	def is_root(self):
		return self.parent == None

class Application(object):
	def __init__(self):
		self._arg_parser = None
		self.argv = sys.argv[1:]
		self.args = None
		self.directory = None

	@property
	def arg_parser(self):
		if self._arg_parser is None:
			parser = argparse.ArgumentParser(
					description="Python Makefile System", 
					prog="pake", add_help=False)
			parser.add_argument(
					'-f', '--file', 
					type=str, default=pake.PAKEFILE_NAME, 
					help='specified a pakefile')
			parser.add_argument(
					'-v', '--verbose', 
					type=int, choices=[0, 1, 2], default=1)
			self._arg_parser = parser
		return self._arg_parser

	def _create_root_pakefile(self):
		pass

	def run(self):
		parser = self.arg_parser
		# parse options --file and --verbose
		self.args, self.argv = parser.parse_known_args(self.argv)
		pake.log.set_verbosity(self.args.verbose)
		parser.add_argument(
				'-h', '--help', 
				action='help', default=argparse.SUPPRESS,
				help=_('show this help message and exit'))
		self.subparser = parser.add_subparsers(help="taget help", dest="target")

		with pake.PakefileContext(self, self.args.file, None):
			self.load()

	def load(self, target=None):
		parser = self.arg_parser
		pakefile = pake.pakefile
		path = pakefile.path
		if not os.path.exists(path):
			raise PakeError('File "%s" is not exists' % path)
		directory, file = os.path.split(path)

		if pakefile.is_root():
			self.directory = directory
			if len(self.argv) == 0:
				target = pakefile.default
			else:
				# get the target name in cmd arguments, fake parse
				args, argv = parser.parse_known_args(self.argv, self.args)
				#task_kwargs = self.args.__dict__
				target = args.target
				#task_kwargs.pop('target')
		else:
			if target is None:
				target = pakefile.default

		old_dir = os.getcwd()
		os.chdir(directory)
		pake.log.info("-"*70)
		pake.log.info(">> %s" % directory)

		pakefile.run_task(target, self.argv)

		pake.log.info("<< %s" % directory)
		pake.log.info("*"*70)
		os.chdir(old_dir)

	def cd(self, path, target=None):
		path = os.path.abspath(path)
		if not os.path.isdir(path):
			raise exceptions.PakeError('Directory "%s" is not exists' % path)
		filepath = os.path.join(path, pake.PAKEFILE_NAME)

		with pake.PakefileContext(self, filepath, pake.pakefile):
			self.load(target)


