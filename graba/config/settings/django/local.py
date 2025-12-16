from .base import *

# These settings extend and override the configurations in base.py.
# Specific options for the development environment are set in this file.

from config.env import env


# ======================================================== #
# =================== Load Environment =================== #
# ======================================================== #

env.read_env(str(ENVS_DIR / '.local.env'))


# ======================================================== #
# =================== Load Environment =================== #
# ======================================================== #

CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

