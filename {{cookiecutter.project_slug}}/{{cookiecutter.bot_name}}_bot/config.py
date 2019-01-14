from _config_section import ConfigSection

import os
from {{cookiecutter.bot_name}}_bot.constant import local_dir

REAL_PATH = local_dir

config = ConfigSection("config")
config.dir = "%s/%s" % (REAL_PATH, "config")

logs = ConfigSection("logs")
logs.dir = "%s/%s" % (REAL_PATH, "logs")
