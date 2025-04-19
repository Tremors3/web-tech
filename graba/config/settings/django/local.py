from .base import *

# These settings extend and override the configurations in base.py.
# Specific options for the development environment are set in this file.

from config.env import env


# ======================================================== #
# =================== Load Environment =================== #
# ======================================================== #

env.read_env(str(ENVS_DIR / '.local.env'))
