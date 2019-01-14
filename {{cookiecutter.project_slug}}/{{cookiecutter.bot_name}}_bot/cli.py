# -*- coding: utf-8 -*-

import click

from {{cookiecutter.bot_name}}_bot.main import run_slackbot
from {{cookiecutter.bot_name}}_bot.main import generate_example_config_file


def main():
    cli.add_command(run_bot)
    cli.add_command(generate_example_config)
    cli()


@click.group()
def cli():
    pass


@click.command()
@click.option('--config_file', default='config.json',
              help='Configuration filepath.')
def run_bot(config_file):
    """Start the bot."""
    run_slackbot(config_file)


@click.command()
def generate_example_config():
    """Generate an example config file."""
    generate_example_config_file()


if __name__ == "__main__":
    main()
