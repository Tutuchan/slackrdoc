# -*- coding: utf-8 -*-
"""
Python Slack Message class for use with the RDocumentation bot
"""
import json



class Message(object):
    """
    Instanciates a Message object to create and manage
    Slack RDocumentation messages.
    """
    def __init__(self):
        super(Message, self).__init__()
        self.channel = ""
        self.timestamp = ""
        self.text = ""
        self.attachments = []

    def create_attachments(self, description, url, fun):
        """
        Open JSON message attachments file and create attachments for
        message. Saves a dictionary of formatted attachments on
        the bot object.
        """
        actions = [{"name": "visit", "type": "button", "text": "View documentation", "url": url}]
        self.attachments = [{"fallback": url, "title": fun, "text": description, "attachment_type": "default", "actions": actions}]
