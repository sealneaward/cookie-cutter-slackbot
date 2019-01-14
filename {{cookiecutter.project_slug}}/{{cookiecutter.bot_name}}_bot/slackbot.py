# -*- coding: utf-8 -*-

import json
import logging
import os
import re
import time
from slackclient import SlackClient

import {{cookiecutter.bot_name}}_bot.message_interpreter as message_interpreter
import {{cookiecutter.bot_name}}_bot.config as CONFIG


class SlackBot(object):
    """The Markov slackbot itself.
    """

    def __init__(self, config):
        """Initialize the Markov slackbot.
        """

        self.logger = logging.getLogger(__name__)
        self.last_ping = 0
        self.commands = self.build_commands()

        log_level = config.get('LOG_LEVEL')
        log_level_name = logging.getLevelName(log_level)
        logging.basicConfig(level=log_level_name)

        self.token = config.get('SLACK_TOKEN')
        self.slack_client = SlackClient(self.token)

    def build_commands(self):
        return {
            "help": lambda channel: self.send_help_message(channel),
            "silence": lambda channel: self.silence(channel),
            "speak": lambda channel: self.unsilence(channel)
        }

    def start(self):
        """Start the bot.
        """

        while True:
            try:
                self.main_loop()

            except Exception:
                self.logger.exception('Fatal error in main loop, restarting.')

    def main_loop(self):
        """The main loop for the bot.
        """

        self.logger.info('Connecting to Slack.')
        self.slack_client.rtm_connect()

        self.logger.info('Setting user info.')
        self.set_user_info()

        self.message_interpreter = message_interpreter.MessageInterpreter(
            self.user_id,
            self.username,
            self.commands.keys()
        )

        self.logger.info('Bot running.')

        while True:
            self.logger.debug('Reading messages.')
            messages = self.slack_client.rtm_read()

            for message in messages:
                self.logger.debug('Retrieved message: {0}'.format(message))

                if (self.message_interpreter.is_respondable(message)):
                    self.logger.debug('Message was respondable, responding.')
                    self.respond(message)

            self.autoping()
            time.sleep(.1)

    def set_user_info(self):
        """Sets the bot's user info so that it can reply to mentions.
        """
        self.username = self.slack_client.server.username
        self.logger.info('Set username: {0}'.format(self.username))

        user = self.slack_client.server.users.find(self.username)
        self.user_id = user.id
        self.logger.info('Set user_id: {0}'.format(self.user_id))

    def respond(self, message):
        """Respond to message.
        """
        try:
            message_text = message['text']
            channel = message['channel']

            commands = self.message_interpreter.find_commands(message_text)

            if commands:
                for command_name in commands:
                    command_name = self.commands[command_name]
                    command_name(channel)
            elif channel not in self.silent_channels:
                masters = self.message_interpreter.find_master(message_text)

                channels = self.message_interpreter.find_channels(message_text)

                self.logger.debug('Finding channel names.')

                channel_names = [self.get_channel_name(channel)
                                 for channel in channels]

                self.logger.debug(
                    'Found channel names: {0}'.format(channel_names))

                users = self.message_interpreter.find_users(message_text)

                response = self.model_controller.build_message(
                    masters,
                    channel_names,
                    users
                )

                self.send_message(channel, response)

        except Exception:
            self.logger.exception('Slack command parsing error.')
            self.send_message(
                message['channel'],
                ("I'm sorry <@{0}>, I'm afraid I can't do" +
                 " that.").format(message['user']))

    def autoping(self):
        """Ping slack every three seconds.
        """

        now = int(time.time())
        if now > self.last_ping + 3:
            self.slack_client.server.ping()
            self.last_ping = now

    def send_message(self, channel, message):
        """Send message to channel.

        :param channel: A slack channel.
        :param message: The message to send.
        """

        self.logger.debug('Sending message: {0}'.format(message))

        self.slack_client.rtm_send_message(channel, message)

    def clean_reply(self, message):
        """Cleans message of mentions and bangs.

        :param message: message to clean.
        :return clean_message: cleaned message.
        """

        mention_pattern = '<@([0-9A-z]+)>'
        bang_pattern = '<!([0-9A-z]+)>'

        self.logger.debug('Cleaning message: {0}'.format(message))

        mentionless_message = re.sub(
            mention_pattern,
            self.replace_mention,
            message)

        self.logger.debug(
            'Removed user mentions, result: {0}'.format(mentionless_message)
        )

        clean_message = re.sub(
            bang_pattern,
            self.replace_bang,
            mentionless_message
        )

        self.logger.debug(
            'Removed bangs, result: {0}'.format(clean_message))

        return clean_message

    def replace_mention(self, match_obj):
        """Replacement for re.sub for mentions. Should maybe replace with
        compiled regex.
        """

        return '@{0}'.format(self.get_username(match_obj.group(1)))

    def replace_bang(match_obj):
        """Replacement for re.sub for mentions. Should maybe replace with
        compiled regex.
        """

        return '!{0}'.format(match_obj.group(1))

    def get_username(self, user_id):
        """Retrieve a username from Slack.

        :param user_id: the id of the user.
        :returns username: the username of the user.
        """

        self.logger.debug('Retrieving username for: {0}'.format(user_id))

        user = self.slack_client.server.users.find(user_id)

        if user is None:
            username = None
            self.logger.warn(
                'Could not find username for: {0}'.format(user_id))
        else:
            username = user.name
            self.logger.debug('Found username: {0}'.format(username))

        return username

    def get_channel_name(self, channel_id):
        """Retrieve a channel name from Slack.

        :param channel_id: the id of the channel.
        :returns channel_name: the name of the channel.
        """

        self.logger.debug(
            'Retrieving channel name for: {0}'.format(channel_id))

        channel = self.slack_client.server.channels.find(channel_id)

        if channel is None:
            channel_name = None
            self.logger.warn(
                'Could not find channel name for: {0}'.format(channel_name))
        else:
            channel_name = channel.name
            self.logger.debug(
                'Found channel name for: {0}'.format(channel_name))

        return channel_name

    def save_silent_channels(self):
        """Save silent channels object.
        """

        silent_channels_json = json.dumps(self.silent_channels, indent=4)

        with open(self.silent_channels_file, 'w') as silent_channels_file:
            silent_channels_file.write(silent_channels_json)

    def send_help_message(self, channel):
        """Send help message. This string should be imported from elsewhere...

        :param channel: channel to send help message to.
        """

        self.logger.debug('Sending help message.')

        message = """There are a few things I can do:

If you say `slack`, or `master`, I will speak using everything I have
learned from slack. This is my default behaviour.

If you say `#channel`, I will speak using everything I have learned
from that channel.

If you say `@user`, I will speak using everything I have learned from
that user.

If you say `$external source`, I will speak using everything I have
learned from that source.

Hint: You can combine multiple commands.
        """

        self.send_message(channel, message)

    def silence(self, channel):
        """Silence bot on a channel.
        """
        if channel not in self.silent_channels:
            self.silent_channels += [channel]
            self.save_silent_channels()
            message = "Okay, I'll be quiet..."
        else:
            message = "I was quiet already. Sorry..."

        self.send_message(channel, message)

    def unsilence(self, channel):
        """Unsilence bot on a channel.
        """
        if channel in self.silent_channels:
            self.silent_channels.remove(channel)
            self.save_silent_channels()
            message = "Thank you!"
        else:
            message = "I wasn't silenced to begin with, silly..."

        self.send_message(channel, message)
