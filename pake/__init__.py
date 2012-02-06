# CONSTANTS
PAKEFILE_NAME = "pakefile.py"
DEFAULT_TASK = "all"
DEFAULT_TYPE = "c"

DEFAULT_BUILD_DIR = "build"
DEFAULT_LIB_DIR = "libs"

class PakeError(Exception):
	pass

from distutils import log
from pake.context import app, pakefile, PakefileContext

