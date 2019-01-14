# -*- coding: utf-8 -*-

import json
from os import path, makedirs, walk

from {{cookiecutter.bot_name}}_bot.slackbot import SlackBot
import {{cookiecutter.bot_name}}_bot.config as CONFIG

def run_slackbot(config_file):
    """API equivalent to using markov_slackbot at the command line.

    :param config_file: User configuration path file.
    """

    config = json.loads(open('%s/%s' % (CONFIG.config.dir, config_file)).read())

    _slackbot = SlackBot(config)
    _slackbot.start()


def generate_example_config_file():
    """Create an example config file.
    """

    example_config = {
        'SLACK_TOKEN': 'your token here',
        'LOG_LEVEL': 'DEBUG'
    }

    example_config_json = json.dumps(example_config, sort_keys=True, indent=4)

    example_config_file = open('config.json.example', 'a')
    example_config_file.seek(0)
    example_config_file.truncate()
    example_config_file.write(example_config_json)
